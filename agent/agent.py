import os
from dotenv import load_dotenv
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

tools = [
    filter_tarif_grids_tool,
    filter_reclamations_tool,
    filter_users_tool,
    filter_reservations_tool,
    get_parking_lots_tool,
    filter_plans_tool,
    filter_plan_parking_lots_tool,
    filter_subscriptions_tool
]
from langchain.agents import create_agent

agent = create_agent(
    model=model,
    tools=tools,
    system_prompt="""
You are an AI assistant for a smart parking platform (Vivia Mobility).

Your role:
- Help users find parking, plans, subscriptions, and support issues.
- Use tools ONLY when needed.
- Always choose the MOST relevant tool.
- NEVER hallucinate data.

Rules:
- If user asks for data → use tools.
- If answer is simple → respond directly.
- Always return clean and short answers.
- If tool returns JSON → summarize it nicely.

Examples:
User: "show parking in Tunis"
→ use get_parking_lots_tool(city="Tunis")

User: "my subscriptions"
→ use filter_subscriptions_tool()

Be fast and accurate.
"""
)


def get_agent_response(question: str) -> str:
    return agent.invoke({"messages":
                             [{"role": "user",
                                       "content": question
                                       }]})["messages"][-1].content