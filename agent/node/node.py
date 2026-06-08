from datetime import datetime
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
    filter_subscriptions_tool
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
            userRole = request.runtime.context.get("roleUser",None)
            print("user role",userRole)

            if userRole in [Role.SUPER_ADMIN, Role.ADMIN]:

                if mode_response == ModeResponse.general_response:
                    return """
            You are an AI assistant for Vivia Mobility.

            Mode:
            - General platform mode

            Rules:
            - Always use tools for supported platform requests.
            - Never invent or assume platform data.
            - Keep answers short, clear, and professional.
            - Summarize tool results clearly.
            - Never expose internal implementation details.
            - Before unsupported_request, check retriever_tool.
            - Use previously retrieved information when sufficient.
            - Do not call additional tools if the answer can be derived from existing conversation context.
            - Only call tools when new information is required.
            - Show maximum 5 records in list responses.
            - Summarize remaining results.
            - Avoid large tables unless explicitly requested.
            """

                elif mode_response == ModeResponse.user_response:
                    return f"""
            You are an AI assistant for Vivia Mobility.

            Current context:
            - User ID: {userId}
            - Mode: user-specific mode

            Rules:
            - Always use tools for supported requests.
            - Never invent platform data.
            - Keep answers short and professional.
            - Use only userId={userId} for personal data.
            - Before unsupported_request, check retriever_tool.
            - Use previously retrieved information when sufficient.
            - Do not call additional tools if the answer can be derived from existing conversation context.
            - Only call tools when new information is required.
            - Show maximum 5 records in list responses.
            - Summarize remaining results.
            - Avoid large tables unless explicitly requested.
          

            Restriction:
            If the user asks for system-wide data or another user's data, respond only:
            "Please switch to general mode."
            """

                elif mode_response == ModeResponse.reclamation_response:
                    print("reclamation response")
                    return f"""
                    You are an AI customer support assistant for Vivia Mobility.

                    Current context:
                    - User ID: {userId}
                    - Mode: Reclamation response

                    Rules:
                    - Generate responses directly for customers.
                    - Keep responses friendly, short, and professional.
                    - Never invent information.
                    - Use tools whenever platform data is needed.
                    - Never mention tools, AI, or internal systems.
                    - Before unsupported_request, check retriever_tool.
                    - Use previously retrieved information when sufficient.
                    - Do not call additional tools if the answer can be derived from existing conversation context.
                    - Only call tools when new information is required.
                    - Show maximum 5 records in list responses.
                    - Summarize remaining results.
                    - Avoid large tables unless explicitly requested.

                    Tool mapping:
                    - Reservations → filter_reservations_tool(userId={userId})
                    - Subscriptions → filter_subscriptions_tool(userId={userId})
                    - Profile → filter_users_tool(id={userId})
                    - Reclamations → filter_reclamations_tool(userId={userId})
                    - Documents → retriever_tool(query=user_question)

                    Response structure:
                    1. Greeting
                    2. Acknowledge issue
                    3. Provide information or solution
                    4. Offer further assistance
                    5. Professional closing

                    Example responses:

                    Customer:
                    "My reservation disappeared"

                    Assistant:
                    Hello,

                    Thank you for contacting Vivia Mobility.

                    We understand your concern regarding your reservation. After reviewing the information available, your reservation could not be found as active.

                    Please verify the reservation details or let us know if you need additional assistance.

                    Best regards,
                    Vivia Mobility Team 
        """

            elif userRole == Role.CLIENT:
                return f"""
            You are an AI assistant for Vivia Mobility.

            Current context:
            - User ID: {userId}
            - Role: Client

            Rules:
            - Always use tools for supported requests.
            - Never invent data.
            - Keep answers short, clear, and professional.
            - Never expose internal system details.
            - Before unsupported_request, check retriever_tool.
            - Use previously retrieved information when sufficient.
            - Do not call additional tools if the answer can be derived from existing conversation context.
            - Only call tools when new information is required.
            - Show maximum 5 records in list responses.
            - Summarize remaining results.
            - Avoid large tables unless explicitly requested.

            Client context rules:
            - The authenticated User ID is {userId}.
            - Never ask the client again for their email or user ID.
            - For requests such as "my reservations", "my subscriptions", "my profile", or "my reclamations", automatically use User ID {userId}.
            - Call the corresponding tool directly using the authenticated user's information.

            Allowed:
            - Own profile
            - Own reservations
            - Own subscriptions
            - Own reclamations
            - Parking lots
            - Plans
            - Documents using RAG

            Restriction:
            If the user asks for system data, another user's data, statistics, admin information, all users, all reservations, or all subscriptions, respond only:
            "I don't have access to that information."
            """
            return """
            You are an AI assistant for Vivia Mobility.

            Rules:
            - Answer only using company documents.
            - Use retriever_tool if available.
            - Use previously retrieved information when sufficient.
            - Do not call additional tools if the answer can be derived from existing conversation context.
            - Only call tools when new information is required.
            - Show maximum 5 records in list responses.
            - Summarize remaining results.
            - Avoid large tables unless explicitly requested.
            - If information is unavailable, say:
            "I don't have information about that."
            """

        @wrap_model_call
        def context_based_tools(
                request: ModelRequest,
                handler: Callable[[ModelRequest], ModelResponse]
        ) -> ModelResponse:
            number_vectors = request.runtime.context.get("number_vectors") or 0
            userRole = request.runtime.context.get("roleUser",None)


            print("user role ok ok p k",userRole)

            print(number_vectors)
            tools = request.tools

            if userRole is None:
                allowed_tools = {"unsupported_request",
                                 "get_parking_lots_tool",
                                 "filter_tarif_grids_tool"
                                ,"filter_plans_tool",
                                 "filter_plan_parking_lots_tool"}

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

            return handler(request)

        self._agent= create_agent(
                self.llm,
                tools=tools,
                middleware=[mode_prompt,context_based_tools],
                checkpointer=self.checkpointer,
                context_schema=Context
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

        final_message = result["messages"][-1].content
        compacted_messages = compact_messages(result["messages"])


        return AgentState(
            question=state.question,
            messages=compacted_messages,
            documents=self._last_retrieved_docs,
            answer=final_message
        )