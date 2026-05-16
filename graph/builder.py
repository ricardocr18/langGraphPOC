"""
builder.py — Monta e compila o grafo LangGraph.

Conceitos aplicados:
  - StateGraph: grafo com estado compartilhado
  - add_node: registra funções Python como nós
  - add_edge: aresta simples (sempre vai de A para B)
  - add_conditional_edges: aresta que escolhe o próximo nó
                           baseada em uma função de roteamento
  - set_entry_point: define por onde o grafo começa
  - compile: valida e congela o grafo para execução
"""

from langgraph.graph import StateGraph, END

from graph.state import TIMAgentState
from guardrails.input_validator import validate_input, route_after_guardrail
from agents.router_agent import tia_router_node, route_after_tia
from agents.info_agent import information_node
from nodes.collect_data import collect_customer_data_node
from nodes.activation import activation_node
from nodes.registro import registro_node


def build_graph():
    """
    Cria, configura e compila o grafo TIM.
    Retorna um CompiledGraph pronto para invocar.
    """
    # 1. Cria o grafo com o tipo do estado
    graph = StateGraph(TIMAgentState)

    # 2. Registra cada nó com um nome único
    #    O nome é o que aparece nas arestas condicionais
    graph.add_node("guardrail_node", validate_input)
    graph.add_node("tia_router_node", tia_router_node)
    graph.add_node("collect_customer_data_node", collect_customer_data_node)
    graph.add_node("information_node", information_node)
    graph.add_node("activation_node", activation_node)
    graph.add_node("registro_node", registro_node)

    # 3. Define o nó de entrada
    graph.set_entry_point("guardrail_node")

    # 4. Aresta condicional: guardrail → TIA ou registro
    graph.add_conditional_edges(
        "guardrail_node",
        route_after_guardrail,
        {
            "tia_router_node": "tia_router_node",
            "registro_node": "registro_node",
        },
    )

    # 5. Aresta condicional: TIA → coleta de dados ou informação
    graph.add_conditional_edges(
        "tia_router_node",
        route_after_tia,
        {
            "collect_customer_data_node": "collect_customer_data_node",
            "information_node": "information_node",
        },
    )

    # 6. Arestas simples (sempre seguem para o mesmo nó)
    graph.add_edge("collect_customer_data_node", "activation_node")
    graph.add_edge("information_node", "registro_node")
    graph.add_edge("activation_node", "registro_node")
    graph.add_edge("registro_node", END)

    # 7. Compila: valida a estrutura e retorna o grafo executável
    return graph.compile()


# Instância global — compilada uma vez
tim_graph = build_graph()