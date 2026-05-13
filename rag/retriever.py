"""
Retriever com busca semântica usando FAISS + OpenAI Embeddings.
Conceitos: embeddings, vector store, similarity search.
"""

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from rag.documents import get_knowledge_documents
from config import OPENAI_API_KEY

import os

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# Instância global do vector store (carregada uma vez)
_vector_store: FAISS | None = None


def _build_vector_store() -> FAISS:
    """Cria o índice FAISS com os documentos TIM."""
    raw_chunks = get_knowledge_documents()

    # Transforma strings em Documents do LangChain
    documents = [
        Document(page_content=chunk, metadata={"source": "tim_knowledge_base"})
        for chunk in raw_chunks
    ]

    # Embeddings da OpenAI (ada-002 por padrão)
    embeddings = OpenAIEmbeddings()

    # Cria o índice vetorial em memória
    vector_store = FAISS.from_documents(documents, embeddings)
    return vector_store


def get_retriever(k: int = 3):
    """
    Retorna o retriever configurado para buscar os k chunks mais relevantes.
    O vector store é construído uma única vez (lazy loading).
    """
    global _vector_store

    if _vector_store is None:
        print("[RAG] Construindo índice vetorial...")
        _vector_store = _build_vector_store()
        print("[RAG] Índice pronto.")

    return _vector_store.as_retriever(search_kwargs={"k": k})


def retrieve_context(query: str, k: int = 3) -> str:
    """
    Busca semântica: dado um texto de consulta, retorna os trechos
    mais relevantes da base de conhecimento TIM.

    Args:
        query: Pergunta ou tópico a buscar
        k: Número de trechos a retornar

    Returns:
        String com os trechos concatenados
    """
    retriever = get_retriever(k=k)
    docs = retriever.invoke(query)

    if not docs:
        return "Nenhuma informação relevante encontrada na base de conhecimento."

    context_parts = []
    for i, doc in enumerate(docs, 1):
        context_parts.append(f"[Trecho {i}]\n{doc.page_content}")

    return "\n\n".join(context_parts)