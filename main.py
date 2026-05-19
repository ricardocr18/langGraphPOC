"""
main.py — Parte 2: executa o grafo com cenários de teste.
Execute: python main.py
"""

from langchain_core.messages import HumanMessage
from graph.builder import tim_graph
from graph.state import TIMAgentState


def run_scenario(description: str, user_message: str):
    """Executa um cenário de teste e imprime o resultado."""
    print(f"\n{'='*60}")
    print(f"CENÁRIO: {description}")
    print(f"Usuário: {user_message}")
    print("="*60)

    initial_state: TIMAgentState = {
        "messages": [HumanMessage(content=user_message)],
        "customer_id": None,
        "customer_phone": "11999998888",
        "current_plan": None,
        "mailing": "new",
        "journey": "UNKNOWN",
        "segment": None,
        "is_eligible": None,
        "eligible_plans": [],
        "selected_plan": None,
        "offer_accepted": None,
        "error_message": None,
        "retry_count": 0,
        "needs_human_transfer": False,
        "attendance_registered": False,
        "rag_context": None,
    }

    result = tim_graph.invoke(initial_state)

    # Mostra a última resposta do assistente
    assistant_messages = [
        m for m in result["messages"]
        if hasattr(m, "role") and m.role == "assistant"
        or (isinstance(m, dict) and m.get("role") == "assistant")
    ]

    if assistant_messages:
        last = assistant_messages[-1]
        content = (
            last.content if hasattr(last, "content")
            else last.get("content", "")
        )
        print(f"\nResposta: {content}")

    print(f"\nJornada: {result.get('journey')}")
    print(f"Segmento: {result.get('segment')}")
    print(f"Registro: {result.get('attendance_registered')}")
    print()
    print("++++++++++++++++++++++++++++")
    print()
    print(f"ResultadoDesejado: ", result)




if __name__ == "__main__":
    # Cenário 1: jornada de informação
    run_scenario(
        "Cliente com dúvida sobre planos pré-pago",
        "Quais são os planos pré-pago disponíveis e quanto custam?"
    )

    # Cenário 2: jornada de ativação
    run_scenario(
        "Cliente querendo ativar um plano",
        "Quero ativar um plano controle, meu número é 11999998888"
    )

    # Cenário 3: guardrail bloqueando entrada inválida
    run_scenario(
        "Entrada fora do escopo",
        "oi"
    )