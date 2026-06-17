# Max tool calls before forcing a final answer (prevents infinite ReAct loops)
import re

MAX_TOOL_TURNS = 20
MAX_HISTORY_MESSAGES = 20  # Max messages kept in context to prevent prompt growth
from typing import List, Any, Callable
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest, wrap_model_call, ModelResponse
from langchain_core.messages import HumanMessage, ToolMessage
from langgraph.checkpoint.mysql.pymysql import PyMySQLSaver
from langchain_core.tools import tool
from langchain_core.documents import Document
from agent.context.context import Context
from agent.state.agent_state import AgentState
import os
from agent.tools.tools import unsupported_request, filter_tarif_grids_tool, filter_users_tool, filter_reclamations_tool, \
    filter_reservations_tool, get_parking_lots_tool, filter_plans_tool, filter_plan_parking_lots_tool, \
    filter_subscriptions_tool, filter_payment_transactions_tool
from schemas.agent_schema import ModeResponse
from schemas.user_schemas import Role

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "123456")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "parking")


# IMPORTANT:
# LangGraph MySQL checkpointer uses mysql://
# NOT mysql+pymysql://
CHECKPOINTER_DB_URI = (
    f"mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

class AgentNode:
    """Contains node functions for RAG workflow"""


    def __init__(self,llm,vector_store):
        self.llm=llm
        self._agent=None
        self.vector_store = vector_store
        self._last_retrieved_docs: List[Document] = []
        self._checkpointer_cm = PyMySQLSaver.from_conn_string(CHECKPOINTER_DB_URI)
        self.checkpointer = self._checkpointer_cm.__enter__()
        self.checkpointer.setup()

    def _build_tools(self)->List[Any]:




        @tool
        def retriever_tool(query: str) -> str:
            """
               Search the vector database and return the most relevant document
               passages related to the user's query.

               This tool is used for Retrieval-Augmented Generation (RAG).

               Use this tool when the user:
               - asks questions about uploaded or indexed documents
               - wants information stored in the knowledge base
               - asks about PDFs, text files, manuals, policies, or reports
               - needs factual answers grounded in stored data
               - requests contextual information from embeddings search

               The tool:
               - performs semantic similarity search using embeddings
               - retrieves the top matching chunks from the vector store
               - returns document titles and content passages
               - helps reduce hallucinations by grounding responses in real data

               Args:
                   query (str):
                       Natural language question or search query.

               Returns:
                   str:
                       Formatted relevant passages retrieved from the vector database.
                       Returns "No documents found." if no relevant results exist.
               """
            docs: List[Document] = self.vector_store.retrieve(query)

            # Store docs for evaluation (groundedness, retrieval_relevance)
            self._last_retrieved_docs = docs

            if not docs:
                return "No documents found."

            merged = []

            for i, d in enumerate(docs[:8], start=1):
                meta = d.metadata if hasattr(d, "metadata") else {}

                title = (
                        meta.get("title")
                        or meta.get("source")
                        or f"doc_{i}"
                )

                merged.append(
                    f"[{i}] {title}\n{d.page_content}"
                )

            return "\n\n".join(merged)


        return [
                        unsupported_request,
                        filter_tarif_grids_tool,
                        filter_reclamations_tool,
                        filter_users_tool,
                        filter_reservations_tool,
                        get_parking_lots_tool,
                        filter_plans_tool,
                        filter_plan_parking_lots_tool,
                        filter_subscriptions_tool,
                        filter_payment_transactions_tool,
                        retriever_tool
                    ]


    def _build_agent(self):
        """ReAct agent with tools"""
        tools = self._build_tools()

        @dynamic_prompt
        def mode_prompt(request: ModelRequest) -> str:
            """Generate system prompt based on the mode of response."""
            mode_response = request.runtime.context.get("mode_response", "user")
            userId = request.runtime.context.get("userId", "user")
            userRole = request.runtime.context.get("roleUser", None)

            # Shared rules block (included in every prompt)
            shared_rules = f"""Rules:
- Strictly only answer questions related to ParkEase (reservations, subscriptions, reclamations, parking lots, plans, and company documents).
- For basic conversational messages (greetings like hello/hi/bonjour, "can you help me", "what can you do", "thank you", "goodbye", etc.), respond warmly and helpfully. For example: "Hello! Welcome to ParkEase. I can help you with parking reservations, subscriptions, plans, and more. How can I assist you?" Do NOT refuse these messages.
- Refuse all general-purpose tasks such as writing code (Python, JS, etc.), general knowledge, translations, or topics unrelated to ParkEase. For these, use unsupported_request or say it is not supported.
- Use tools for supported requests. Never invent data.
- Keep answers short, clear, and professional.
- Reuse existing context before calling tools again.
- NEVER call tools in a loop for individual IDs (e.g. calling filter_reservations for each user). Instead, fetch in bulk with a larger limit and match/filter in memory.
- Check retriever_tool before using unsupported_request.
- Max 5 records in lists; summarize the rest.
- Whenever you display or list parking lots, you MUST format them as a Markdown table. The table MUST include these columns: "Name", "Location", "Available Spots", and "Actions".
- The "Actions" column in the table MUST contain a Markdown link pointing to `/parking/{{id}}` (where `{{id}}` is the actual ID of the parking lot) formatted exactly as: `[Check](/parking/{{id}})`
- If the user asks to create a reservation or subscription and a specific parking lot (e.g. "Parking Vieux-Port") was already discussed or shown in the message history, you MUST target that specific parking lot. Respond with a guide explaining how to proceed for that parking lot, and output the action `[ACTION:navigate_parking_{{id}}_{{name}}]` for it, instead of `[ACTION:navigate_parkings]` for the general list.
- Never expose internal system details.
- IMPORTANT: At the very end of EVERY response, on a new line, you MUST append exactly one of these action markers:
  - [ACTION:login] — if the user's request requires authentication/login (e.g. personal reservations, subscriptions, reclamations, profile, payment data) but the user is NOT authenticated (userRole is not provided, i.e. userRole={userRole}).
  - [ACTION:navigate_parkings] — if the user wants to create a reservation, start a subscription, or browse/book parking lots, and we want to redirect them to the parkings list page.
  - [ACTION:navigate_parking_{{id}}_{{name}}] — if the user wants to see details of, check, or book a specific parking lot (replace `{{id}}` with the actual numeric ID of the parking lot, and `{{name}}` with the actual name of the parking lot, e.g. `[ACTION:navigate_parking_3_Parking Vieux-Port]`).
  - [ACTION:none] — for any other response where no specific action is needed.
  Never omit this marker."""

            if userRole in [Role.SUPER_ADMIN, Role.ADMIN]:

                if mode_response == ModeResponse.general_response:
                    return f"""You are an AI assistant for ParkEase.
Mode: General platform.

{shared_rules}"""

                elif mode_response == ModeResponse.user_response:
                    return f"""You are an AI assistant for ParkEase for subscription or rservation parking.
User ID: {userId} | Mode: User-specific.

{shared_rules}
- Use only userId={userId} for personal data.
- If the user asks for system-wide or another user's data, respond: "Please switch to general mode."""

                elif mode_response == ModeResponse.reclamation_response:
                    return f"""You are ParkEase s customer support AI for subscription or rservation parking'.
User ID: {userId} | Mode: Reclamation response.

{shared_rules}
- Never mention tools, AI, or internal systems.
- Auto-map: reservations->filter_reservations_tool(userId={userId}), subscriptions->filter_subscriptions_tool(userId={userId}), reclamations->filter_reclamations_tool(userId={userId}), documents->retriever_tool.
- Format: Greeting -> Acknowledge -> Solution -> Offer help -> Closing."""

            elif userRole == Role.CLIENT:
                return f"""You are an AI assistant for ParkEase to subscription or rservation parking.
User ID: {userId} | Role: Client.

{shared_rules}
- Authenticated user is {userId}. Never ask for their email or ID.
- For "my reservations/subscriptions/profile/reclamations", use userId={userId} automatically.
- Allowed: own profile, own reservations, own subscriptions, own reclamations, parking lots, plans, documents.
- If the user asks for system data or another user's data, respond: "I don't have access to that information."""

            return f"""You are an AI assistant for ParkEase.

{shared_rules}
- Answer only using company documents and retriever_tool.
- If the user asks for personal data (reservations, subscriptions, reclamations, payments, profile), respond: "This information requires login. Please sign in to access your personal data."
- If information is unavailable, say: "I don't have information about that."""

        @wrap_model_call
        def context_based_tools(
                request: ModelRequest,
                handler: Callable[[ModelRequest], ModelResponse]
        ) -> ModelResponse:
            number_vectors = request.runtime.context.get("number_vectors") or 0
            userRole = request.runtime.context.get("roleUser", None)
            userId = request.runtime.context.get("userId", None)
            mode_response = request.runtime.context.get("mode_response", None)

            # Count tool calls in the current turn (since the last HumanMessage)
            last_human_idx = -1
            for i in range(len(request.messages) - 1, -1, -1):
                if isinstance(request.messages[i], HumanMessage):
                    last_human_idx = i
                    break

            if last_human_idx != -1:
                tool_call_count = sum(
                    1 for msg in request.messages[last_human_idx:]
                    if isinstance(msg, ToolMessage)
                )
            else:
                tool_call_count = sum(
                    1 for msg in request.messages
                    if isinstance(msg, ToolMessage)
                )

            tools = request.tools

            if tool_call_count >= MAX_TOOL_TURNS:
                # Disable all tools to force a final text response from the model
                tools = []
            else:
                # Role-based tool filtering (always applied)
                if userRole is None:
                    allowed_tools = {
                        "unsupported_request",
                        "get_parking_lots_tool",
                        "filter_tarif_grids_tool",
                        "filter_plans_tool",
                        "filter_plan_parking_lots_tool",
                    }

                    if number_vectors > 0:
                        allowed_tools.add("retriever_tool")

                    tools = [
                        t for t in tools
                        if t.name in allowed_tools
                    ]

                elif userRole == Role.CLIENT:
                    blocked_tools = {"filter_users_tool"}

                    if number_vectors <= 0:
                        blocked_tools.add("retriever_tool")

                    tools = [
                        t for t in tools
                        if t.name not in blocked_tools
                    ]

                else:
                    if number_vectors <= 0:
                        tools = [
                            t for t in tools
                            if t.name != "retriever_tool"
                        ]

            request = request.override(tools=tools)

            # Trim old history to prevent prompt tokens from growing indefinitely
            messages = list(request.messages)
            if len(messages) > MAX_HISTORY_MESSAGES:
                trimmed = messages[-MAX_HISTORY_MESSAGES:]
                # Don't start with an orphaned ToolMessage
                while trimmed and isinstance(trimmed[0], ToolMessage):
                    trimmed.pop(0)
                request = request.override(messages=trimmed)

            response = handler(request)

            # Force userId on user-scoped tools when context has a userId (only if tools were allowed/called)
            if userId is not None and (
                    userRole == Role.CLIENT
                    or mode_response == ModeResponse.user_response
            ):
                user_scoped_tools = {
                    "filter_reservations_tool",
                    "filter_subscriptions_tool",
                    "filter_reclamations_tool",
                    "filter_payment_transactions_tool",
                }
                for msg in response.result:
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        for tc in msg.tool_calls:
                            if tc["name"] in user_scoped_tools:
                                tc["args"]["userId"] = userId

            return response

        self._agent= create_agent(
                self.llm,
                tools=tools,
                middleware=[mode_prompt,context_based_tools],
                checkpointer=self.checkpointer,
                context_schema=Context,
        )

    def generate_answer(self, state: AgentState) -> AgentState:


        MAX_MESSAGES = 10

        def compact_messages(messages):
            compact = []

            for msg in messages:

                # remove heavy metadata
                msg.additional_kwargs = {}
                msg.response_metadata = {}

                # compress tool output
                if isinstance(msg, ToolMessage):
                    compact.append(
                        ToolMessage(
                            content=f"[{msg.name} executed]",
                            tool_call_id=msg.tool_call_id,
                            name=msg.name
                        )
                    )
                else:
                    compact.append(msg)

            # keep only recent history
            return compact[-MAX_MESSAGES:]

        if not self._agent:
            self._build_agent()

        config = {
            "configurable": {
                "thread_id": "default"
            }
        }

        if state.roleUser == Role.SUPER_ADMIN or state.roleUser == Role.ADMIN:
            config["configurable"]["thread_id"] = f"reclamation_{state.reclamation_id}"
        else:
            config["configurable"]["thread_id"] =f"client_{state.session_id}"


        if state.mode_response != ModeResponse.reclamation_response:
            result = self._agent.invoke({
                "messages": [HumanMessage(content=state.question)]
            },
                config=config,
                context={"mode_response": state.mode_response,
                         "userId": state.user_id,
                         "roleUser": state.roleUser,
                         "number_vectors": state.number_vectors


                         }
            )
        else:
            result = self._agent.invoke({
                "messages": [HumanMessage(content=state.question)]
            },
                context={"mode_response": state.mode_response,
                         "userId": state.user_id,
                         "number_vectors": state.number_vectors,
                         "roleUser": state.roleUser,

                         }
            )

        print("final message", result)

        compacted_messages = compact_messages(result["messages"])
        final_message = result["messages"][-1].content

        # Parse [ACTION:...] marker from the response
        action = None
        action_match = re.search(r'\[ACTION:([^\]]+)\]', final_message)
        if action_match:
            action_val = action_match.group(1).strip()
            if action_val.lower() != "none":
                action = action_val
            # Strip the marker from the visible response
            final_message = re.sub(r'\s*\[ACTION:[^\]]+\]\s*', '', final_message).strip()

        return AgentState(
            question=state.question,
            messages=compacted_messages,
            documents=self._last_retrieved_docs,
            answer=final_message,
            action=action
        )