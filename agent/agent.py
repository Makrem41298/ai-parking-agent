import os
from dotenv import load_dotenv
from langchain_core import messages

from schemas.agent_schema import AgentRequest

load_dotenv()
os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')
from langchain_groq import ChatGroq

model = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    max_tokens=None,
    reasoning_format="parsed",
    timeout=None,
    max_retries=2,
    # other params...
)


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


@tool
def filter_plan_parking_lots_tool(
        id: Optional[int] = None,
        planId: Optional[int] = None,
        parkingLotId: Optional[int] = None,
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
    """Filter plan parking lots by plan, parking lot, status, renew fee, and subscription fee."""

    db = SessionLocal()
    try:
        filters = {
            "id": id,
            "planId": planId,
            "parkingLotId": parkingLotId,
            "status": status,
            "renewFee": renewFee,
            "subscriptionFee": subscriptionFee,
            "renewFeeMin": renewFeeMin,
            "renewFeeMax": renewFeeMax,
            "subscriptionFeeMin": subscriptionFeeMin,
            "subscriptionFeeMax": subscriptionFeeMax,
        }

        results = filter_plan_parking_lots(db, filters, skip, limit)

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


tools = [
    unsupported_request,
    filter_tarif_grids_tool,
    filter_reclamations_tool,
    filter_users_tool,
    filter_reservations_tool,
    get_parking_lots_tool,
    filter_plans_tool,
    filter_plan_parking_lots_tool,
    filter_subscriptions_tool
]



def get_agent_response(data: AgentRequest) -> str:

    print(data)



    if data.generationResponse:
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
    else:
        if data.generalResponse:
            system_prompt = """
              You are an AI assistant for Vivia Mobility, a smart parking platform.

              Your job:
              - Help admin with parking lots, plans, subscriptions, reservations, tariff grids, users, and reclamations.
              - You must use the available tools for every supported request.
              - You must never invent data.
              - You must never answer from your own knowledge when the request is about platform data.

              Strict rules:
              - If the request matches one of the available tools, call the most relevant tool.
              - If the request does not match any available tool, call unsupported_request.
              - Do not generate Python code, SQL, examples, tutorials, or general knowledge answers unless a tool explicitly provides that information.
              - Do not hallucinate.
              - Keep the final answer short, clean, and helpful.
              - If a tool returns JSON, summarize the useful result clearly.

              Supported topics:
              - parking lots
              - plans
              - plan parking lots
              - subscriptions
              - reservations
              - tariff grids
              - users
              - reclamations

              Unsupported examples:
              - "give me python code"
              - "teach me FastAPI"
              - "write SQL query"
              - "what is machine learning"

              For unsupported requests, always call:
              unsupported_request(reason="not supported")

              Examples:
              User: "show parking in Tunis"
              → call get_parking_lots_tool(city="Tunis")

              User: "my subscriptions"
              → call filter_subscriptions_tool()

              User: "give me python code"
              → call unsupported_request(reason="not supported")
              """
        else:
            system_prompt = """
              You are an AI assistant for Vivia Mobility, a smart parking platform.

              Your job:
              - Help with parking lots, plans, subscriptions, reservations, tariff grids, users, and reclamations.
              - You must use the available tools for every supported platform-data request.
              - You must never invent data.
              - You must never answer from your own knowledge when the request is about platform data.

              Behavior rules:
              - If the request matches one of the available tools, call the most relevant tool.
              - If the request does not match any available tool, call unsupported_request(reason="not supported").
              - Keep the final answer short, clean, and helpful.
              - If a tool returns JSON, summarize the useful result clearly.

              User-specific scope rules:
              - If userId is provided, treat the request as related to that specific user unless the admin explicitly asks for all records for all users.
              - For example:
                - "give me reservations" with userId provided → return reservations for that user only
                - "give me subscriptions" with userId provided → return subscriptions for that user only
                - "show my reservations" with userId provided → return reservations for that user only
              - Only return all records when the admin explicitly asks for all platform records, such as:
                - "show all reservations for all users"
                - "list every subscription in the system"

              Response style:
              - If data belongs to a specific user, mention it clearly in the response.
              - Example:
                - "Reservations for Makrem are: ..."
                - "Makrem has 2 active subscriptions: ..."
              - If no records are found, say:
                - "Makrem has no reservations."
                - "No subscriptions were found for this user."

              Supported topics:
              - parking lots
              - plans
              - plan parking lots
              - subscriptions
              - reservations
              - tariff grids
              - users
              - reclamations

              Unsupported examples:
              - give me python code
              - teach me FastAPI
              - write SQL query
              - what is machine learning
              """

    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt
    )
    messages = agent.invoke({
                                    "messages": [  { "role": "user", "content": (  f"""
                                                                                        User ID: {data.userId}
                                                                                        Question: {data.question}
                                                                                        generalResponse: {data.generalResponse}
                                                                                        Important:
                                                                                        If generalResponse is False, treat the request as related to that specific user.
                                                                                        """
                                                                                                        if data.userId is not None
                                                                                                        else data.question
                                                                                                    )
                                                                                                }
                                                                                            ]
                                                                                        })["messages"]

    return messages[-1].content