"""
Servidor FastAPI que simula a API de elegibilidade da TIM.
Execute em terminal separado: uvicorn tools.mock_api_server:app --port 8001

Conceito: HTTP dinâmico — a URL e os parâmetros são montados
em tempo de execução baseados no estado do cliente.
"""

from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel

app = FastAPI(title="TIM Eligibility API Mock")


# Banco mockado de elegibilidade
_ELIGIBILITY_DB = {
    "TIM-001": {
        "eligible": True,
        "reason": None,
        "plans": [
            {
                "id": "controle-30",
                "name": "TIM Controle 30",
                "price": 30.00,
                "internet": "10GB",
                "highlight": "10GB + streaming incluso",
                "segment": "CONTROLE",
            },
            {
                "id": "controle-50",
                "name": "TIM Controle 50",
                "price": 50.00,
                "internet": "20GB",
                "highlight": "20GB + Disney+ incluso",
                "segment": "CONTROLE",
            },
        ],
    },
    "TIM-002": {
        "eligible": False,
        "reason": "Débito em aberto. Regularize para continuar.",
        "plans": [],
    },
}

_ACTIVATION_LOG = []


class ActivationRequest(BaseModel):
    customer_id: str
    plan_id: str
    agent: str = "TIA"


@app.get("/eligibility")
def check_eligibility(customer_id: str = Query(...)):
    """Consulta elegibilidade do cliente."""
    if customer_id not in _ELIGIBILITY_DB:
        # Cliente desconhecido: retorna elegível com plano básico
        return {
            "eligible": True,
            "reason": None,
            "plans": [
                {
                    "id": "pre-top",
                    "name": "TIM Pré Top",
                    "price": 15.00,
                    "internet": "1GB",
                    "highlight": "Ideal para começar",
                    "segment": "PRE_PAGO",
                }
            ],
        }
    return _ELIGIBILITY_DB[customer_id]


@app.post("/activate")
def activate_plan(request: ActivationRequest):
    """Registra a ativação de um plano."""
    if request.customer_id not in _ELIGIBILITY_DB:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    db_entry = _ELIGIBILITY_DB[request.customer_id]
    plan_ids = [p["id"] for p in db_entry.get("plans", [])]

    if request.plan_id not in plan_ids:
        raise HTTPException(
            status_code=400,
            detail=f"Plano {request.plan_id} não elegível para este cliente"
        )

    record = {
        "customer_id": request.customer_id,
        "plan_id": request.plan_id,
        "agent": request.agent,
        "status": "ACTIVATED",
    }
    _ACTIVATION_LOG.append(record)

    return {
        "success": True,
        "protocol": f"TIM-{request.customer_id}-{request.plan_id}".upper(),
        "message": f"Plano {request.plan_id} ativado com sucesso!",
    }


@app.get("/activations")
def list_activations():
    """Lista ativações realizadas (para debug)."""
    return _ACTIVATION_LOG