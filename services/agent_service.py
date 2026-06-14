import os
import shutil
from datetime import datetime
from typing import List
from fastapi.responses import FileResponse

from dotenv import load_dotenv
from fastapi import UploadFile, File, HTTPException, BackgroundTasks
from langchain_groq import ChatGroq

from agent.parsing.document_processor import DocumentProcessor
from schemas.DeleteFilesRequest import DeleteFilesRequest
from schemas.agent_schema import AgentRequest
from agent.vectorstore.vectorstore import VectorStore
from agent.graph.graph_builder import GraphBuilder


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing in .env file")

os.environ["GROQ_API_KEY"] = GROQ_API_KEY


model = ChatGroq(
    model="openai/gpt-oss-20b",
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
    print(f"number of vectors: {vector_store.count_vectors()}")
    result = graph_builder.run_graph(
        question=data.question,
        user_id=data.userId,
        roleUser=data.roleUser,
        reclamation_id=data.reclamationId,
        session_id=data.sessionId,
        mode_response=data.mode_response,
        number_vectors=vector_store.count_vectors()

    )


    return result.get("answer", "")


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


processor = DocumentProcessor()


def upload_file(  background_tasks: BackgroundTasks,files: List[UploadFile] = File(...)):

    folders = {
        "pdf": "agent/data/pdf",
        "csv": "agent/data/csv",
        "xlsx": "agent/data/excel",
        "xls": "agent/data/excel",
        "doc": "agent/data/word",
        "docx": "agent/data/word",
        "ppt": "agent/data/powerpoint",
        "pptx": "agent/data/powerpoint",
        "txt": "agent/data/text",
        "json": "agent/data/json",
    }

    saved_files = []

    for file in files:

        extension = file.filename.split(".")[-1].lower()

        upload_dir = folders.get(
            extension,
            "agent/data/others"
        )

        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(
            upload_dir,
            file.filename
        )

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        saved_files.append({
            "filename": file.filename,
            "path": file_path,
            "type": extension
        })
        background_tasks.add_task(rebuild_vectorstore)



    return {
        "message": "Files saved successfully",
        "files": saved_files
    }

BASE_DIR = "agent/data"
def download_file(filename: str):

    for root, dirs, files in os.walk(BASE_DIR):

        for file in files:

            if file == filename:

                file_path = os.path.join(root, file)

                return FileResponse(
                    path=file_path,
                    filename=file,
                    media_type="application/octet-stream"
                )
    raise HTTPException(
        status_code=404,
        detail="File not found"
    )





vectorstore_status = {
    "status": "idle"
}

def rebuild_vectorstore():

    try:
        vector_store.reset_collection()
        pdf_docs = processor.process_pdf_folder("agent/data/pdf")
        txt_docs = processor.process_text_folder("agent/data/text", extension=".txt")
        word_docs = processor.process_word_folder("agent/data/word")
        csv_docs = processor.process_csv_folder("agent/data/csv")
        excel_docs = processor.process_excel_folder("agent/data/excel")
        json_docs = processor.process_json_folder("agent/data/json", mode="text", )
        
        vectorstore_status["status"] = "processing"
        print("Loading documents...")
        docs = pdf_docs + txt_docs + word_docs + csv_docs + excel_docs + json_docs
        print(f"Loaded {len(docs)} documents")
        vector_store.create_vectorstore(
            docs=docs,
            save_chunks=True
        )
        vector_store.setup()
        vectorstore_status["status"] = "completed"

        print("Vectorstore rebuilt successfully")

    except Exception as e:

        vectorstore_status["status"] = "failed"
        vectorstore_status["error"] = str(e)

        print(f"Vectorstore rebuild failed: {e}")



def delete_files_service(
    data: DeleteFilesRequest,
    background_tasks: BackgroundTasks
):
    deleted_files = []
    not_found = []

    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file in data.filenames:
                file_path = os.path.join(root, file)
                os.remove(file_path)
                deleted_files.append(file)

    for filename in data.filenames:
        if filename not in deleted_files:
            not_found.append(filename)

    background_tasks.add_task(rebuild_vectorstore)

    return {
        "message": "Delete process completed. Vectorization started.",
        "deleted": deleted_files,
        "notFound": not_found
    }






