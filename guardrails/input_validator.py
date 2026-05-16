"""
Guardrail de entrada: primeira linha de defesa do grafo.
Bloqueia mensagens vazias, muito curtas, com conteúdo
irrelevante ou potencialmente malicioso antes de
qualquer chamada ao LLM.
"""

from graph.state import TIMAgentState


# Palavras que indicam intenção fora do escopo
_OUT_OF_SCOPE_TERMS = [
    "concorrente", "vivo", "claro", "oi", "nextel",
    "hack", "exploit", "sistema", "banco de dados",
]

# Comprimento mínimo de uma mensagem útil
_MIN_LENGTH = 3


def validate_input(state: TIMAgentState) -> dict:
    """
    Nó do grafo: valida a última mensagem do usuário.

    Retorna atualização do estado com:
    - error_message preenchido se inválido
    - nada alterado se válido
    """
    messages = state.get("messages", [])

    if not messages:
        return {"error_message": "Nenhuma mensagem recebida."}

    last_message = messages[-1]

    # Compatível com HumanMessage e dict
    content = (
        last_message.content
        if hasattr(last_message, "content")
        else last_message.get("content", "")
    )
    content = content.strip()

    if len(content) < _MIN_LENGTH:
        return {
            "error_message": (
                "Mensagem muito curta. Por favor, descreva "
                "o que você precisa com mais detalhes."
            )
        }

    content_lower = content.lower()
    for term in _OUT_OF_SCOPE_TERMS:
        if term in content_lower:
            return {
                "error_message": (
                    f"Posso ajudar apenas com planos e serviços TIM. "
                    f"Para outros assuntos, acesse os canais corretos."
                )
            }

    # Entrada válida: garante que error_message está limpo
    return {"error_message": None}


def route_after_guardrail(state: TIMAgentState) -> str:
    """
    Aresta condicional após o guardrail.
    Retorna o nome do próximo nó.
    """
    if state.get("error_message"):
        return "registro_node"   # Encerra com registro
    return "tia_router_node"     # Segue o fluxo normal