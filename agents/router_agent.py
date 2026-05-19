"""
TIA — Agente roteador principal.
Responsabilidades:
  1. Entender o que o cliente quer
  2. Buscar contexto no RAG
  3. Decidir a jornada: INFORMATION ou ACTIVATION
  4. Extrair dados básicos do cliente se presentes

Conceito LangGraph: este é um nó com chamada ao LLM.
O LLM lê o estado e retorna uma decisão estruturada.
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from graph.state import TIMAgentState
from rag.retriever import retrieve_context
from config import OPENAI_API_KEY

import os
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


# --- Schema da resposta do LLM (saída estruturada) ---

class RouterDecision(BaseModel):
    journey: str = Field(
        description="INFORMATION se o cliente quer informação, "
                    "ACTIVATION se quer ativar ou trocar de plano"
    )
    segment: str = Field(
        description="PRE_PAGO, CONTROLE ou POS_PAGO baseado no contexto. "
                    "UNKNOWN se não for possível identificar."
    )
    customer_phone: str = Field(
        description="Número de telefone mencionado pelo cliente, ou '' se não houver."
    )
    reasoning: str = Field(
        description="Breve explicação da decisão tomada (1 frase)."
    )


_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
_parser = JsonOutputParser(pydantic_object=RouterDecision)


def tia_router_node(state: TIMAgentState) -> dict:
    """
    Nó do grafo: agente TIA.
    Lê as mensagens, consulta o RAG e decide a jornada.
    """
    messages = state.get("messages", [])
    last_message = messages[-1]
    content = (
        last_message.content    # HumanMessage (objeto)
        if hasattr(last_message, "content")
        else last_message.get("content", "")    # dict simples
    )

    # Busca semântica: contexto relevante para a solicitação
    rag_context = retrieve_context(content, k=2)

    system_prompt = f"""Você é a TIA, assistente virtual da TIM.
Sua função é entender a solicitação do cliente e classificá-la.

Contexto da base de conhecimento TIM:
{rag_context}

Responda APENAS em JSON válido seguindo o formato:
{_parser.get_format_instructions()}

Regras de classificação:
- ACTIVATION: cliente quer ativar plano, fazer upgrade, trocar plano, migrar
- INFORMATION: dúvidas sobre planos, preços, cobertura, serviços, faturas

Se o segmento não for mencionado, use UNKNOWN."""

    response = _llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=content),
    ])

    try:
        decision = _parser.parse(response.content)
    except Exception:
        # Fallback seguro se o LLM não retornar JSON válido
        decision = {
            "journey": "INFORMATION",
            "segment": "UNKNOWN",
            "customer_phone": "",
            "reasoning": "Não foi possível classificar. Assumindo jornada de informação.",
        }

    print(f"[TIA] Decisão: {decision}")

    updates = {
        "journey": decision.get("journey", "INFORMATION"),
        "segment": decision.get("segment", "UNKNOWN"),
        "rag_context": rag_context,
    }

    phone = decision.get("customer_phone", "")
    if phone:
        updates["customer_phone"] = phone

    return updates


def route_after_tia(state: TIMAgentState) -> str:
    """
    Aresta condicional após TIA.
    Mapeia a jornada para o próximo nó.
    """
    journey = state.get("journey", "INFORMATION")

    if journey == "ACTIVATION":
        return "collect_customer_data_node"

    # INFORMATION e UNKNOWN vão para o nó de informação diretamente
    return "information_node"