import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from schemas.agent_schema import AgentRequest
from agent.vectorstore.vectorstore import VectorStore
from agent.graph.graph_builder import GraphBuilder


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing in .env file")

os.environ["GROQ_API_KEY"] = GROQ_API_KEY


model = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    reasoning_format="parsed",
    max_retries=2,
)


vector_store = VectorStore()
vector_store.setup()

graph_builder = GraphBuilder(
    llm=model,
    vector_store=vector_store
)


def get_agent_response(data: AgentRequest) -> str:
    result = graph_builder.run_graph(
        question=data.question,
        user_id=data.userId,
        reclamation_id=data.reclamationId,
        mode_response=data.mode_response,
    )

    return result.get("answer", "")