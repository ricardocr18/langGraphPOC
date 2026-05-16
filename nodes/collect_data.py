"""
Nó de coleta de dados.
Em produção: chamaria uma API de CRM para buscar dados do cliente.
Aqui: extrai dados da conversa e simula a busca.

Conceito LangGraph: nó sem LLM — lógica Python pura que
atualiza campos específicos do estado.
"""

from graph.state import TIMAgentState


# Simulação de banco de clientes (em produção: chamada ao CRM)
_MOCK_CUSTOMERS = {
    "11999998888": {
        "customer_id": "TIM-001",
        "current_plan": "TIM Pré Top",
        "mailing": "old",
        "segment": "PRE_PAGO",
    },
    "11988887777": {
        "customer_id": "TIM-002",
        "current_plan": None,
        "mailing": "new",
        "segment": "UNKNOWN",
    },
}


def collect_customer_data_node(state: TIMAgentState) -> dict:
    """
    Nó do grafo: busca dados do cliente pelo telefone.
    Se não encontrar, mantém os dados como None
    para o agente pedir ao cliente.
    """
    phone = state.get("customer_phone", "")

    if not phone:
        print("[Coleta] Telefone não identificado ainda.")
        return {}   # Nada muda no estado

    # Normaliza o telefone (remove formatação)
    phone_clean = "".join(filter(str.isdigit, phone))[-11:]

    customer = _MOCK_CUSTOMERS.get(phone_clean)

    if customer:
        print(f"[Coleta] Cliente encontrado: {customer['customer_id']}")
        return {
            "customer_id": customer["customer_id"],
            "current_plan": customer["current_plan"],
            "mailing": customer["mailing"],
            # Preserva o segmento identificado pelo TIA se o CRM não souber
            "segment": customer["segment"] or state.get("segment", "UNKNOWN"),
        }

    print(f"[Coleta] Cliente não encontrado para telefone {phone_clean}.")
    return {"mailing": "new"}   # Cliente novo não cadastrado