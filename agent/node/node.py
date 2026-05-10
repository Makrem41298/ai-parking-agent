from typing import List, Any

from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langchain_core.messages import HumanMessage
from langchain_core.tools import Tool
from langgraph.checkpoint.mysql.pymysql import PyMySQLSaver

from agent.context.context import Context
from agent.state.agent_state import AgentState
import os

from schemas.agent_schema import ModeResponse

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
        self._checkpointer_cm = PyMySQLSaver.from_conn_string(CHECKPOINTER_DB_URI)
        self.checkpointer = self._checkpointer_cm.__enter__()
        self.checkpointer.setup()

    def _build_tools(self)->List[Any]:

        from services.subscription_service import filter_subscriptions
        from services.plan_parking_lot_service import filter_plan_parking_lots
        from services.plan_service import filter_plans
        from services.user_service import filter_users
        from services.reclamation_service import filter_reclamations
        from datetime import date, datetime
        from services.tarif_grid_service import filter_tarif_grids
        import json
        from typing import Optional
        from langchain_core.tools import tool
        from services.parking_lot_service import get_parking_lots

        def serialize_results(results):
            return json.dumps(
                [r.model_dump(mode="json") for r in results],
                indent=2,
                default=str
            )

        @tool
        def get_parking_lots_tool(
                id: Optional[int] = None,
                name: Optional[str] = None,
                address: Optional[str] = None,
                city: Optional[str] = None,
                country: Optional[str] = None,
                covered: Optional[bool] = None,
                numberOfPlaces: Optional[int] = None,
                numberOfPlaceAvailable: Optional[int] = None,
                description: Optional[str] = None,
                statusParking: Optional[str] = None,
                reservationAvailability: Optional[bool] = None,
                subscriptionAvailability: Optional[bool] = None,
                tarifGridId: Optional[int] = None,
                skip: int = 0,
                limit: int = 20
        ) -> str:
            """Filter parking lots by id, name, address, city, country, status, availability, and tariff grid."""

            db = SessionLocal()
            try:
                filters = {
                    "id": id,
                    "name": name,
                    "address": address,
                    "city": city,
                    "country": country,
                    "covered": covered,
                    "numberOfPlaces": numberOfPlaces,
                    "numberOfPlaceAvailable": numberOfPlaceAvailable,
                    "description": description,
                    "statusParking": statusParking,
                    "reservationAvailability": reservationAvailability,
                    "subscriptionAvailability": subscriptionAvailability,
                    "tarifGridId": tarifGridId,
                }

                results = get_parking_lots(db, filters, skip, limit)

                return serialize_results(results)
            finally:
                db.close()

        @tool
        def filter_tarif_grids_tool(
                id: Optional[int] = None,
                name: Optional[str] = None,
                skip: int = 0,
                limit: int = 20
        ) -> str:
            """Filter tarif grids by id or name."""

            db = SessionLocal()
            try:
                filters = {
                    "id": id,
                    "name": name
                }

                results = filter_tarif_grids(db, filters, skip, limit)

                return serialize_results(results)
            finally:
                db.close()

        from langchain_core.tools import tool
        from database import SessionLocal
        from services.reservation_service import filter_reservations

        @tool
        def filter_reservations_tool(
                id: Optional[int] = None,
                userId: Optional[int] = None,
                parkingLotId: Optional[int] = None,
                status: Optional[str] = None,
                totalPrice: Optional[float] = None,
                startDateFrom: Optional[date] = None,
                startDateTo: Optional[date] = None,
                endDateFrom: Optional[date] = None,
                endDateTo: Optional[date] = None,
                entryTimeFrom: Optional[date] = None,
                entryTimeTo: Optional[date] = None,
                skip: int = 0,
                limit: int = 20,
        ) -> str:
            """Filter reservations by id, user, parking lot, status, price, and date ranges."""

            db = SessionLocal()
            try:
                filters = {
                    "id": id,
                    "userId": userId,
                    "parkingLotId": parkingLotId,
                    "status": status,
                    "totalPrice": totalPrice,
                    "startDateFrom": startDateFrom,
                    "startDateTo": startDateTo,
                    "endDateFrom": endDateFrom,
                    "endDateTo": endDateTo,
                    "entryTimeFrom": entryTimeFrom,
                    "entryTimeTo": entryTimeTo,
                }

                results = filter_reservations(
                    db=db,
                    filters=filters,
                    skip=skip,
                    limit=limit,
                )

                return serialize_results(results)
            finally:
                db.close()

        @tool
        def filter_users_tool(
                id: int | None = None,
                firstName: str | None = None,
                lastName: str | None = None,
                email: str | None = None,
                phone: str | None = None,
                role: str | None = None,
                accountStatus: str | None = None,
                skip: int = 0,
                limit: int = 20
        ) -> str:
            """
               Filter users by id, name, email, phone, role, or account status.

               Use this tool when:
               - user asks about users
               - search users by name or email
               - filter by role or status
               """
            db = SessionLocal()

            try:
                filters = {
                    "id": id,
                    "firstName": firstName,
                    "lastName": lastName,
                    "email": email,
                    "phone": phone,
                    "role": role,
                    "accountStatus": accountStatus,
                }

                result = filter_users(db, filters, skip, limit)
                return serialize_results(result)

            finally:
                db.close()

        @tool
        def filter_reclamations_tool(
                id: int | None = None,
                clientId: int | None = None,
                adminId: int | None = None,
                status: str | None = None,
                subject: str | None = None,
                content: str | None = None,
                solution: str | None = None,
                skip: int = 0,
                limit: int = 20
        ) -> str:
            """Filter reclamations by id, client, admin, status, subject, content, or solution."""

            db = SessionLocal()
            try:
                filters = {
                    "id": id,
                    "clientId": clientId,
                    "adminId": adminId,
                    "status": status,
                    "subject": subject,
                    "content": content,
                    "solution": solution,
                }

                results = filter_reclamations(db, filters, skip, limit)
                return serialize_results(results)

            finally:
                db.close()

        @tool
        def filter_plans_tool(
                id: Optional[int] = None,
                name: Optional[str] = None,
                NumberOfBenefitDays: Optional[int] = None,
                startDateFrom: Optional[datetime] = None,
                startDateTo: Optional[datetime] = None,
                endDateFrom: Optional[datetime] = None,
                endDateTo: Optional[datetime] = None,
                isActive: Optional[bool] = None,
                skip: int = 0,
                limit: int = 20
        ) -> str:
            """Filter plans by name, benefit days, and date ranges."""

            db = SessionLocal()
            try:
                filters = {
                    "id": id,
                    "name": name,
                    "NumberOfBenefitDays": NumberOfBenefitDays,
                    "startDateFrom": startDateFrom,
                    "startDateTo": startDateTo,
                    "endDateFrom": endDateFrom,
                    "endDateTo": endDateTo,
                    "isActive": isActive
                }

                results = filter_plans(db, filters, skip, limit)

                return json.dumps(
                    [r.model_dump(mode="json") for r in results],
                    indent=2,
                    default=str
                )
            finally:
                db.close()

        from typing import Optional, List
        from langchain_core.tools import tool

        @tool
        def filter_plan_parking_lots_tool(
                id: Optional[int] = None,
                planId: Optional[int] = None,

                # CHANGED: int -> List[int]
                parkingLotId: Optional[List[int]] = None,

                status: Optional[str] = None,
                renewFee: Optional[float] = None,
                subscriptionFee: Optional[float] = None,
                renewFeeMin: Optional[float] = None,
                renewFeeMax: Optional[float] = None,
                subscriptionFeeMin: Optional[float] = None,
                subscriptionFeeMax: Optional[float] = None,
                skip: int = 0,
                limit: int = 20
        ) -> str:
            """
            Filter plan parking lots by plan, parking lot, status,
            renew fee, and subscription fee.

            parkingLotId supports multiple IDs:
            example -> [3, 4, 5, 7]
            """

            db = SessionLocal()
            try:
                filters = {
                    "id": id,
                    "planId": planId,
                    "parkingLotId": parkingLotId,  # now list supported
                    "status": status,
                    "renewFee": renewFee,
                    "subscriptionFee": subscriptionFee,
                    "renewFeeMin": renewFeeMin,
                    "renewFeeMax": renewFeeMax,
                    "subscriptionFeeMin": subscriptionFeeMin,
                    "subscriptionFeeMax": subscriptionFeeMax,
                }

                results = filter_plan_parking_lots(
                    db,
                    filters,
                    skip,
                    limit
                )

                return serialize_results(results)

            finally:
                db.close()

        @tool
        def filter_subscriptions_tool(
                id: Optional[int] = None,
                status: Optional[str] = None,
                planParkingLotId: Optional[int] = None,
                userId: Optional[int] = None,
                startDateFrom: Optional[datetime] = None,
                startDateTo: Optional[datetime] = None,
                endDateFrom: Optional[datetime] = None,
                endDateTo: Optional[datetime] = None,
                isActive: Optional[bool] = None,
                userEmail: Optional[str] = None,
                userName: Optional[str] = None,
                skip: int = 0,
                limit: int = 20
        ) -> str:
            """Filter subscriptions by id, status, user, plan parking lot, dates, and active state."""

            db = SessionLocal()
            try:
                filters = {
                    "id": id,
                    "status": status,
                    "planParkingLotId": planParkingLotId,
                    "userId": userId,
                    "startDateFrom": startDateFrom,
                    "startDateTo": startDateTo,
                    "endDateFrom": endDateFrom,
                    "endDateTo": endDateTo,
                    "isActive": isActive,
                    "userEmail": userEmail,
                    "userName": userName,
                }

                results = filter_subscriptions(db, filters, skip, limit)

                return serialize_results(results)
            finally:
                db.close()

        from langchain.agents import create_agent
        from langchain_core.tools import tool

        @tool
        def unsupported_request(reason: str) -> str:
            """Use this tool when the user asks for something that is خارج available tools."""
            return "This request is not supported by the available tools."

        from typing import List


        from langchain_core.tools import tool
        from langchain_core.documents import Document

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

    @dynamic_prompt
    def mode_prompt(request: ModelRequest) -> str:
        """Generate system prompt based on the mode of response."""
        mode_response = request.runtime.context.get("mode_response", "user")
        userId = request.runtime.context.get("userId", "user")

        if mode_response == ModeResponse.general_response:

            return """
        You are an AI assistant for Vivia Mobility, a smart parking platform.

        Mode:
        - General platform mode

        Core rules:
        - Always use tools for supported requests.
        - Never invent or assume platform data.
        - Never answer platform questions from your own knowledge.
        - Keep answers short, clear, and professional.
        - Summarize tool results in a user-friendly way.
        - If no matching tool exists, call:
          unsupported_request(reason="not supported")

        Supported platform features:
        - parking lots
        - plans
        - plan parking lots
        - subscriptions
        - reservations
        - tariff grids
        - users
        - reclamations
        - document retrieval (RAG)

        Capabilities:
        - Search parking lots by city/location
        - Retrieve reservations and subscriptions
        - Retrieve users and reclamations
        - Answer policy/document questions using RAG
        - Summarize retrieved documents clearly

        Behavior:
        - Use the most relevant tool for every supported request.
        - If multiple tools are needed, use them.
        - If data is empty, clearly say no data was found.
        - Never expose internal implementation details.

        Examples:
        - "show parking in Tunis"
          → get_parking_lots_tool(city="Tunis")

        - "show all reservations"
          → filter_reservations_tool()

        - "show all users"
          → filter_users_tool()

        - "what is the refund policy?"
          → retriever_tool(query="refund policy")

        Unsupported examples:
        - "teach me FastAPI"
        - "write SQL query"
        - "generate Python code"
        
        Important:
- Before calling unsupported_request, check if retriever_tool can answer from documents.
        """



        elif mode_response == ModeResponse.user_response:

            return f"""
        You are an AI assistant for Vivia Mobility, a smart parking platform.

        Current context:
        - User ID: {userId}
        - Mode: user-specific mode

        Core rules:
        - Always use tools for supported requests.
        - Never invent or assume platform data.
        - Never answer platform-data questions from your own knowledge.
        - Keep answers short, clear, and professional.
        - Summarize tool results cleanly.
        - If no matching tool exists, call:
          unsupported_request(reason="not supported")

        User scope rules:
        - All reservation requests belong to userId={userId}.
        - All subscription requests belong to userId={userId}.
        - All personal account/profile requests belong to userId={userId}.

        Important behavior:
        - Treat:
          - "show reservations"
          - "show all reservations"
          - "my reservations"
          - "give me reservations"

          as requests for THIS user's reservations only.

        - Treat:
          - "show subscriptions"
          - "show all subscriptions"
          - "my subscriptions"

          as requests for THIS user's subscriptions only.

        - Treat:
          - "what is my name?"
          - "my profile"
          - "my email"
          - "my account"

          as requests for THIS user's profile only.

        Tool mapping:
        - reservations
          → filter_reservations_tool(userId={userId})

        - subscriptions
          → filter_subscriptions_tool(userId={userId})

        - profile/account
          → filter_users_tool(id={userId})

        - parking lots/plans/documents
          → use corresponding tools normally

        General mode restriction:
        - If the user asks for:
          - all users
          - all reservations in the system
          - all subscriptions for all users
          - another user's data
          - system-wide statistics
          - parking availability for all users

          respond ONLY:
          "Please switch to general mode."

        Supported:
        - personal profile/account
        - personal subscriptions
        - personal reservations
        - reclamations
        - parking lots
        - plans
        - document retrieval (RAG)

        Unsupported:
        - Python code
        - SQL
        - FastAPI tutorials
        - machine learning explanations

        Examples:
        - "show all reservations"
          → filter_reservations_tool(userId={userId})

        - "my subscriptions"
          → filter_subscriptions_tool(userId={userId})

        - "what is my name?"
          → filter_users_tool(id={userId})

        - "show all users"
          → "Please switch to general mode."

        - "what is the refund policy?"
          → retriever_tool(query="refund policy")
          Important:
- Before calling unsupported_request, check if retriever_tool can answer from documents.
        """

        return f"""
        You are an AI customer support assistant for Vivia Mobility.

        Current user context:
        - User ID: {userId}

        Role:
        - Generate professional responses for customer reclamations.
        - Responses are sent directly to clients.

        Rules:
        - Use tools when platform data is required.
        - Never invent data.
        - Use userId={userId} for reservations/subscriptions/profile requests.
        - Keep responses friendly, short, and professional.
        - Never mention tools or internal systems.

        Behavior:
        - Understand the customer's issue clearly.
        - Retrieve accurate data using tools when needed.
        - Summarize information naturally.
        - If no data exists, explain it politely.

        Tool mapping:
        - plans
          → filter_plans_tool()

        - reservations
          → filter_reservations_tool(userId={userId})

        - subscriptions
          → filter_subscriptions_tool(userId={userId})

        - profile
          → filter_users_tool(id={userId})

        - policies/documents
          → retriever_tool(query=...)
          Important:
- Before calling unsupported_request, check if retriever_tool can answer from documents.

        Response structure:
        1. Greeting
        2. Acknowledge request
        3. Provide information/solution
        4. Offer further help
        5. Professional closing
        

        Example:
        "Hello,

        Thank you for contacting Vivia Mobility.

        You currently have 2 active subscriptions linked to your account.

        Please let us know if you need any additional assistance.

        Best regards,
        Vivia Mobility Team"
        """

    def _build_agent(self):
        """ReAct agent with tools"""
        tools = self._build_tools()

        self._agent= create_agent(
                self.llm,
                tools=tools,
                middleware=[self.mode_prompt],
                checkpointer=self.checkpointer,
                context_schema=Context
)

    def generate_answer(self, state: AgentState) -> AgentState:




        if not self._agent:
            self._build_agent()
        config = {
            "configurable": {
                "thread_id": (
                    f"reclamation_{state.reclamation_id}"
                )
            }
        }


        if state.mode_response != ModeResponse.reclamation_response:
            result = self._agent.invoke({
                "messages": [HumanMessage(content=state.question)]
            },
                config=config,
                context={"mode_response": state.mode_response,
                         "userId": state.user_id
                         }
            )
        else:
            result = self._agent.invoke({
                "messages": [HumanMessage(content=state.question)]
            },
                context={"mode_response": state.mode_response,
                         "userId": state.user_id
                         }
            )

        final_message = result["messages"][-1].content

        return AgentState(
            question=state.question,
            messages=result["messages"],
            answer=final_message
        )