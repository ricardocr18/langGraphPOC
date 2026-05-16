"""
Nó de registro: último nó antes do END.
Responsável por gravar o resultado do atendimento.
Em produção: chamaria a API de CRM/ticketing.
"""

from graph.state import TIMAgentState
import datetime


def registro_node(state: TIMAgentState) -> dict:
    """
    Registra o atendimento e prepara o encerramento.
    """
    journey = state.get("journey", "INFORMATION")
    customer_id = state.get("customer_id", "anônimo")
    offer_accepted = state.get("offer_accepted")
    error_msg = state.get("error_message")

    # Define o tipo de registro conforme o resultado
    if error_msg:
        result = "BLOQUEADO_GUARDRAIL"
    elif journey == "ACTIVATION" and offer_accepted:
        result = "ATIVACAO"
    elif journey == "ACTIVATION" and offer_accepted is False:
        result = "ATIVACAO_RECUSADA"
    else:
        result = "INFORMACAO"

    registro = {
        "timestamp": datetime.datetime.now().isoformat(),
        "customer_id": customer_id,
        "journey": journey,
        "result": result,
        "error": error_msg,
    }

    print(f"[Registro] Atendimento registrado: {registro}")

    return {
        "attendance_registered": True,
        "messages": [{
            "role": "assistant",
            "content": (
                "Atendimento encerrado. Protocolo registrado. "
                "Obrigado por contatar a TIM!"
            ),
        }],
    }