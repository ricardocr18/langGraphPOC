"""
Agente de informação: responde dúvidas usando o RAG.
Conceito: nó LLM com contexto recuperado do vector store.
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from graph.state import TIMAgentState
from rag.retriever import retrieve_context
from config import OPENAI_API_KEY

import os
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)


def information_node(state: TIMAgentState) -> dict:
    """
    Nó do grafo: responde ao cliente com base no RAG.
    Atualiza as mensagens com a resposta do agente.
    """
    messages = state.get("messages", [])
    last_message = messages[-1]
    content = (
        last_message.content
        if hasattr(last_message, "content")
        else last_message.get("content", "")
    )

    # Usa o contexto já recuperado pelo TIA, ou busca novamente
    rag_context = state.get("rag_context") or retrieve_context(content, k=3)

    error_msg = state.get("error_message")
    if error_msg:
        # Cliente foi bloqueado pelo guardrail — informa educadamente
        response_text = (
            f"Olá! {error_msg} Como posso ajudar com "
            f"planos e serviços TIM?"
        )
    else:
        system_prompt = f"""Você é a TIA, assistente virtual da TIM.
Responda de forma clara, objetiva e amigável.
Use apenas as informações abaixo para responder.
Se não souber, diga que vai verificar.

Informações TIM:
{rag_context}"""

        response = _llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=content),
        ])
        response_text = response.content

    print(f"[Info] Resposta gerada ({len(response_text)} chars)")

    return {
        "messages": [{"role": "assistant", "content": response_text}],
        "attendance_registered": False,
    }