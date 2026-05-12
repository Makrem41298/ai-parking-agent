from datetime import datetime
import os
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from starlette.concurrency import run_in_threadpool

from schemas.DeleteFilesRequest import DeleteFilesRequest
from services import agent_service
from services.agent_service import get_agent_response, upload_file, vectorstore_status
from auth.auth_bearer import JWTBearer
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



@api_router.post(("/save-files"),dependencies=[Depends(JWTBearer())])
async def save_files(background_tasks: BackgroundTasks,files: List[UploadFile] = File(...)):
    return upload_file(background_tasks,files=files)



@api_router.get("/files")
def get_files():

    BASE_DIR = "agent/data"

    files_data = []
    file_id = 1

    for root, dirs, files in os.walk(BASE_DIR):

        for file in files:

            file_path = os.path.join(root, file)

            stats = os.stat(file_path)

            files_data.append({
                "id": file_id,
                "filename": file,
                "size": stats.st_size,
                "createdAt": datetime.fromtimestamp(
                    stats.st_ctime
                ).isoformat()
            })

            file_id += 1

    return {
        "files": files_data
    }

@api_router.post("/files/delete-batch")
def delete_files_route(
    data: DeleteFilesRequest,
    background_tasks: BackgroundTasks
):
    return agent_service.delete_files_service(
        data,
        background_tasks
    )
@api_router.get("/files/{filename}/download")
def download_file(filename: str):

    return  agent_service.download_file(filename)


@api_router.get("/vectorstore/status")
def get_vectorstore_status():
    return vectorstore_status


