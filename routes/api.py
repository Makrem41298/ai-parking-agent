from fastapi import APIRouter, Depends, HTTPException, Query, Header
from starlette.concurrency import run_in_threadpool

from agent.agent import get_agent_response
from auth.auth_bearer import JWTBearer
from auth.auth_handler import decodeJWT
from schemas.agent_schema import AgentRequest

api_router = APIRouter()

@api_router.get("/")
async def welcome():
    return {"message": "Hello World"}



@api_router.post("/agent",dependencies=[Depends(JWTBearer())])
async def agent(data: AgentRequest):



    print(data)

    answer = await run_in_threadpool(get_agent_response, data)


    return {"question": data.question,
            "answer": answer
            }