"""
main.py — Parte 1: valida RAG e estado inicial.
Execute: python main.py
"""

from graph.state import TIMAgentState
from rag.retriever import retrieve_context


def test_rag():
    print("=== Teste RAG — Busca Semântica ===\n")

    queries = [
        "Quais planos estão disponíveis para clientes pré-pago?",
        "Qual é o processo de ativação de um plano?",
        "Quando devo transferir para atendimento humano?",
    ]

    for query in queries:
        print(f"Consulta: {query}")
        context = retrieve_context(query)
        print(f"Resultado:\n{context[:300]}...\n")
        print("-" * 60)


def test_state():
    print("\n=== Teste Estado Inicial ===\n")

    # Criando um estado inicial como o grafo criaria
    initial_state: TIMAgentState = {
        "messages": [],
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

    print("Estado criado com sucesso:")
    for key, value in initial_state.items():
        print(f"  {key}: {value!r}")


if __name__ == "__main__":
    test_state()
    test_rag()