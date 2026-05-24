from datetime import datetime
import os
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy.sql import roles
from starlette.concurrency import run_in_threadpool

from schemas.DeleteFilesRequest import DeleteFilesRequest
from schemas.user_schemas import Role
from services import agent_service
from services.agent_service import get_agent_response, upload_file, vectorstore_status
from auth.auth_bearer import JWTBearer
from schemas.agent_schema import AgentRequest

api_router = APIRouter()

@api_router.get("/")
async def welcome():
    return {"message": "Hello World"}

@api_router.post("/agent")
async def agent(data: AgentRequest,    user: dict = Depends(JWTBearer())):
    print(data)
    data.roleUser = user.get("role")
    if data.roleUser == Role.CLIENT:
        data.userId=user.get("id")

    print(data)
    answer = await run_in_threadpool(get_agent_response, data)
    return {"question": data.question,
            "answer": answer
            }

@api_router.post("/agent-anonymous")
async def agent(data: AgentRequest):
    print(data)
    data.roleUser = None
    print(data)
    answer = await run_in_threadpool(get_agent_response, data)
    return {"question": data.question,
            "answer": answer
            }





@api_router.post(("/save-files"),dependencies=[Depends(JWTBearer())])
async def save_files(background_tasks: BackgroundTasks,files: List[UploadFile] = File(...)):
    return upload_file(background_tasks,files=files)



@api_router.get("/files",dependencies=[Depends(JWTBearer())])
def get_files():

    return agent_service.get_files()

@api_router.post("/files/delete-batch",dependencies=[Depends(JWTBearer())])
def delete_files_route(
    data: DeleteFilesRequest,
    background_tasks: BackgroundTasks
):
    return agent_service.delete_files_service(
        data,
        background_tasks
    )
@api_router.get("/files/{filename}/download",dependencies=[Depends(JWTBearer())])
def download_file(filename: str):

    return  agent_service.download_file(filename)


@api_router.get("/vectorstore/status",dependencies=[Depends(JWTBearer())])
def get_vectorstore_status():
    return vectorstore_status


