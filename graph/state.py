# Este é o coração do LangGraph.
# Todo agente lê e escreve neste estado compartilhado.

from typing import Annotated, Literal, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class TIMAgentState(TypedDict):
    """
    Estado compartilhado entre todos os nós do grafo.
    Cada campo representa uma informação que os agentes precisam
    ler ou modificar durante a jornada do cliente.
    """

    # --- Mensagens da conversa (acumuladas automaticamente) ---
    messages: Annotated[list, add_messages]

    # --- Dados do cliente ---
    customer_id: Optional[str]          # ID do cliente TIM
    customer_phone: Optional[str]       # Número de telefone
    current_plan: Optional[str]         # Plano atual do cliente
    mailing: Literal["new", "old"]      # Novo ou antigo cliente

    # --- Jornada e roteamento ---
    journey: Literal["INFORMATION", "ACTIVATION", "UNKNOWN"]
    segment: Optional[str]              # Pré-Pago, Controle, Pós-Pago

    # --- Elegibilidade e oferta ---
    is_eligible: Optional[bool]         # Resultado da API de elegibilidade
    eligible_plans: list[dict]          # Planos disponíveis para o cliente
    selected_plan: Optional[dict]       # Plano escolhido pelo cliente
    offer_accepted: Optional[bool]      # Cliente aceitou a oferta?

    # --- Controle de fluxo ---
    error_message: Optional[str]        # Mensagem de erro, se houver
    retry_count: int                    # Contador de tentativas
    needs_human_transfer: bool          # Transferir para atendente humano?
    attendance_registered: bool         # Registro de atendimento feito?

    # --- RAG: contexto recuperado ---
    rag_context: Optional[str]          # Trechos recuperados do conhecimento