"""
Nó de ativação — stub para Parte 2.
Na Parte 3 este nó chamará a API de elegibilidade.
"""

from graph.state import TIMAgentState


def activation_node(state: TIMAgentState) -> dict:
    """
    Stub: sinaliza que o cliente quer ativar um plano.
    A lógica real de elegibilidade vem na Parte 3.
    """
    customer_id = state.get("customer_id", "desconhecido")
    segment = state.get("segment", "UNKNOWN")

    print(f"[Ativação] Cliente {customer_id} | Segmento: {segment}")
    print("[Ativação] Aguardando implementação da API (Parte 3).")

    return {
        "messages": [{
            "role": "assistant",
            "content": (
                "Identificamos sua solicitação de ativação de plano. "
                "Vou verificar as opções disponíveis para você. "
                "Um momento..."
            ),
        }]
    }