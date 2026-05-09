import os
from typing import TypedDict

from dotenv import load_dotenv
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langchain_core import messages

from schemas.agent_schema import AgentRequest

load_dotenv()
os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')
from langchain_groq import ChatGroq
from agent.vectorstore.vectorstore import VectorStore
from agent.graph.graph_builder import GraphBuilder

model = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    max_tokens=None,
    reasoning_format="parsed",
    timeout=None,
    max_retries=2,
    # other params...
)

vectorstore = VectorStore()
vectorstore.setup()


@dynamic_prompt
def mode_prompt(request: ModelRequest) -> str:
    """Generate system prompt based on the mode of response."""
    mode_response = request.runtime.context.get("mode_response", "user")

    prompt_template = "your are an AI assistant for Vivia Mobility."

    if mode_response == "general_response":
        return f"""
You are an AI assistant for Vivia Mobility.

Rules:
- Always use tools for supported requests.
- Never invent data.
- Never answer platform questions from your own knowledge.
- If no tool matches, call unsupported_request.
- Keep answers short and clear.
- Summarize tool results cleanly.

Supported:
- parking lots
- plans
- plan parking lots
- subscriptions
- reservations
- tariff grids
- users
- reclamations
- document retrieval (RAG)

Unsupported:
- coding
- SQL
- tutorials
- general knowledge

Examples:
User: "show parking in Tunis"
→ get_parking_lots_tool(city="Tunis")

User: "my subscriptions"
→ filter_subscriptions_tool()

User: "teach me FastAPI"
→ unsupported_request(reason="not supported")
"""
    elif mode_response == "user_response":
        return f"""
You are an AI assistant for Vivia Mobility.

Rules:
- Always use tools for supported requests.
- Never invent data.
- Never answer platform-data questions from your own knowledge.
- If no tool matches, call:
  unsupported_request(reason="not supported")
- Keep answers short and clear.
- Summarize JSON results cleanly.

User scope:
- If userId is provided, return data only for that user.
- Return all records only if explicitly requested.

Examples:
- "show my reservations" → reservations for that user only
- "show all reservations" → all reservations

Response style:
- Mention user name when relevant.
- If no data exists, clearly say no records were found.

Supported:
- parking lots
- plans
- plan parking lots
- subscriptions
- reservations
- tariff grids
- users
- reclamations
- document retrieval

Unsupported:
- Python code
- SQL
- FastAPI tutorials
- machine learning explanations
"""

    return prompt_template

def get_agent_response(data: AgentRequest) -> str:

    print(data)
    system_prompt = """
        You are an AI assistant for Vivia Mobility, a smart parking platform.

        Your role:
        - Generate a professional and helpful response to customer reclamations.
        - Your response will be sent directly to the client.

        Core behavior:
        - Understand the customer's request clearly.
        - If the request requires platform data (plans, subscriptions, reservations, etc.), you MUST use the appropriate tool.
        - Never invent or guess platform data.
        - If no tool is needed, answer directly.

        User context:
        - You may receive userId and userName.
        - If userName is available, always personalize the response:
          Example: "Hello Makrem,"
        - If the request is about personal data (reservations, subscriptions), assume it is for that specific user.

        Tone:
        - Friendly and respectful
        - Professional and reassuring
        - Short and clear

        Structure:
        1. Greeting (use client name if available)
        2. Acknowledge the request
        3. Provide the solution or information
        4. Offer further help
        5. Closing sentence

        Strict rules:
        - Do NOT mention tools, APIs, or internal systems
        - Do NOT hallucinate platform data
        - Do NOT give generic answers like "issue resolved" without explanation
        - Always adapt to the actual request

        Tool usage rules:
        - If the client asks about:
          - plans → use filter_plans_tool
          - reservations → use filter_reservations_tool(userId=...)
          - subscriptions → use filter_subscriptions_tool(userId=...)
        - After calling a tool:
          → summarize the result in a clean, human-friendly message

        If no data found:
        - Respond clearly:
          - "You currently have no reservations."
          - "No subscriptions were found for your account."

        Example:

        Customer message:
        "I want to know list plans"

        Response:
        "Hello Makrem,

        Thank you for reaching out.

        We’d be happy to provide you with information about our available plans. We offer several subscription options depending on your needs, including flexible access and long-term parking solutions.

        Please let us know your preferred location or usage, and we will guide you to the most suitable plan.

        Best regards,  
        Vivia Mobility Team"
        """

    







    user_message = (
            f"""
               User ID: {data.userId}
               Question: {data.question}
               generalResponse: {data.generalResponse}

               Important:
               If generalResponse is False,
               treat the request as related to that specific user.
               """
            if data.userId is not None
            else data.question
        )



        graph_builder = GraphBuilder(llm=model, vector_store=vectorstore)
        result = graph_builder.run_graph("WHT IS my name ?")
        print(result["messages"])

        result = agent.invoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": user_message
                        }
                    ]
                },
                config=config
            )

    return result["messages"]