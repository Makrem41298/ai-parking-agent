import os
import pickle
import hashlib
from typing import List, Optional

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever


class VectorStore:
    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        chunks_path: str = "./chunks.pkl",
        collection_name: str = "test_collection",
        model_name: str = "BAAI/bge-m3",
        device: str = "cuda",
    ):
        self.persist_directory = persist_directory
        self.chunks_path = chunks_path
        self.collection_name = collection_name

        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": device},
            encode_kwargs={
                "batch_size": 1,
                "normalize_embeddings": True,
            },
        )

        self.vectorstore: Optional[Chroma] = None
        self.dense_retriever = None
        self.bm25_retriever = None
        self.hybrid_retriever = None
        self.docs: Optional[List[Document]] = None

    def _make_ids(self, docs: List[Document]) -> List[str]:
        ids = []

        for doc in docs:
            file_name = doc.metadata.get("file", "unknown")
            page = doc.metadata.get("page", 0)
            chunk_index = doc.metadata.get("chunk_index", 0)

            raw_id = f"{file_name}-{page}-{chunk_index}-{doc.page_content[:100]}"
            stable_id = hashlib.md5(raw_id.encode("utf-8")).hexdigest()
            ids.append(stable_id)

        return ids

    def save_chunks_file(self, docs: List[Document]) -> None:
        folder = os.path.dirname(self.chunks_path)

        if folder:
            os.makedirs(folder, exist_ok=True)

        with open(self.chunks_path, "wb") as file:
            pickle.dump(docs, file)

        print(f"Saved {len(docs)} chunks to {self.chunks_path}")

    def load_chunks_file(self) -> List[Document]:
        if not os.path.exists(self.chunks_path):
            raise FileNotFoundError(f"Chunks file not found: {self.chunks_path}")

        with open(self.chunks_path, "rb") as file:
            self.docs = pickle.load(file)

        print(f"Loaded {len(self.docs)} chunks")

        self.bm25_retriever = BM25Retriever.from_documents(self.docs)
        self.bm25_retriever.k = 5

        return self.docs

    def create_vectorstore(self, docs: List[Document], save_chunks: bool = True) -> Chroma:
        os.makedirs(self.persist_directory, exist_ok=True)

        if save_chunks:
            self.save_chunks_file(docs)

        ids = self._make_ids(docs)

        self.vectorstore = Chroma.from_documents(
            documents=docs,
            embedding=self.embeddings,
            ids=ids,
            persist_directory=self.persist_directory,
            collection_name=self.collection_name,
        )

        print(f"Vector store created with {self.vectorstore._collection.count()} vectors")
        print(f"Persisted to: {self.persist_directory}")

        return self.vectorstore

    def load_vectorstore(self) -> Chroma:
        if not os.path.exists(self.persist_directory):
            raise FileNotFoundError(f"Chroma folder not found: {self.persist_directory}")

        self.vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
            collection_name=self.collection_name,
        )

        self.dense_retriever = self.vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": 3,
                "fetch_k": 20,
                "lambda_mult": 0.8,
                "filter": {"type": "text"},
            },
        )

        print(f"Loaded Chroma with {self.vectorstore._collection.count()} vectors")

        return self.vectorstore

    def build_hybrid_retriever(
        self,
        bm25_weight: float = 0.4,
        dense_weight: float = 0.6,
    ):
        if self.bm25_retriever is None:
            raise ValueError("BM25 retriever not initialized. Call load_chunks_file() first.")

        if self.dense_retriever is None:
            raise ValueError("Dense retriever not initialized. Call load_vectorstore() first.")

        total = bm25_weight + dense_weight

        if total <= 0:
            raise ValueError("Weights must be positive.")

        bm25_weight = bm25_weight / total
        dense_weight = dense_weight / total

        self.hybrid_retriever = EnsembleRetriever(
            retrievers=[
                self.bm25_retriever,
                self.dense_retriever,
            ],
            weights=[
                bm25_weight,
                dense_weight,
            ],
        )

        return self.hybrid_retriever

    def setup(self):
        self.load_chunks_file()
        self.load_vectorstore()
        return self.build_hybrid_retriever()

    def retrieve(self, query: str):
        if self.hybrid_retriever is None:
            raise ValueError("Hybrid retriever not initialized. Call setup() first.")

        return self.hybrid_retriever.invoke(query)