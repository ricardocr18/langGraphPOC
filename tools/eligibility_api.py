"""
Cliente HTTP dinâmico para a API de elegibilidade.

Conceitos aplicados:
  - HTTPX: cliente HTTP assíncrono/síncrono com timeout configurável
  - HTTP dinâmico: URL e parâmetros montados em tempo de execução
  - Tratamento de erros HTTP: timeout, 4xx, 5xx com mensagens claras
  - Retry automático com backoff (sem biblioteca externa)
"""

import httpx
import time
from config import ELIGIBILITY_API_URL


# Configurações do cliente HTTP
_TIMEOUT = httpx.Timeout(
    connect=3.0,    # Tempo máximo para conectar
    read=10.0,      # Tempo máximo para ler resposta
    write=5.0,      # Tempo máximo para enviar dados
    pool=2.0,       # Tempo máximo para obter conexão do pool
)

_MAX_RETRIES = 2
_RETRY_DELAY = 1.0  # segundos entre tentativas


def _build_eligibility_url(customer_id: str) -> str:
    """
    HTTP dinâmico: constrói a URL em tempo de execução.
    Em produção a base URL viria do config por ambiente
    (dev, staging, prod) e o customer_id do estado.
    """
    return f"{ELIGIBILITY_API_URL}?customer_id={customer_id}"


def check_eligibility(customer_id: str) -> dict:
    """
    Consulta a API de elegibilidade com retry automático.

    Retorna dict com:
        eligible (bool): cliente pode ativar plano
        plans (list): planos disponíveis
        reason (str | None): motivo se inelegível
        error (str | None): mensagem de erro técnico
    """
    url = _build_eligibility_url(customer_id)
    last_error = None

    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            print(f"[API] Tentativa {attempt}/{_MAX_RETRIES} → {url}")

            with httpx.Client(timeout=_TIMEOUT) as client:
                response = client.get(url)

            # 2xx: sucesso
            if response.status_code == 200:
                data = response.json()
                print(f"[API] Elegibilidade: {data.get('eligible')} "
                      f"| Planos: {len(data.get('plans', []))}")
                return {
                    "eligible": data.get("eligible", False),
                    "plans": data.get("plans", []),
                    "reason": data.get("reason"),
                    "error": None,
                }

            # 4xx: erro do cliente — não faz retry
            if 400 <= response.status_code < 500:
                msg = f"Erro {response.status_code}: {response.text}"
                print(f"[API] Erro cliente: {msg}")
                return {
                    "eligible": False,
                    "plans": [],
                    "reason": None,
                    "error": msg,
                }

            # 5xx: erro do servidor — faz retry
            last_error = f"Servidor retornou {response.status_code}"

        except httpx.ConnectTimeout:
            last_error = "Timeout ao conectar na API de elegibilidade"
            print(f"[API] {last_error}")

        except httpx.ReadTimeout:
            last_error = "Timeout ao ler resposta da API de elegibilidade"
            print(f"[API] {last_error}")

        except httpx.ConnectError:
            last_error = "API de elegibilidade indisponível"
            print(f"[API] {last_error}")

        except Exception as e:
            last_error = f"Erro inesperado: {str(e)}"
            print(f"[API] {last_error}")

        # Aguarda antes do próximo retry (exceto na última tentativa)
        if attempt < _MAX_RETRIES:
            print(f"[API] Aguardando {_RETRY_DELAY}s antes de retry...")
            time.sleep(_RETRY_DELAY)

    # Todas as tentativas falharam
    return {
        "eligible": False,
        "plans": [],
        "reason": None,
        "error": last_error or "API indisponível após todas as tentativas",
    }


def activate_plan(customer_id: str, plan_id: str) -> dict:
    """
    Posta a ordem de ativação do plano escolhido.

    Retorna dict com:
        success (bool): ativação realizada
        protocol (str | None): protocolo gerado
        error (str | None): mensagem de erro
    """
    activate_url = ELIGIBILITY_API_URL.replace("/eligibility", "/activate")

    try:
        with httpx.Client(timeout=_TIMEOUT) as client:
            response = client.post(
                activate_url,
                json={
                    "customer_id": customer_id,
                    "plan_id": plan_id,
                    "agent": "TIA",
                },
            )

        if response.status_code == 200:
            data = response.json()
            print(f"[API] Ativação OK | Protocolo: {data.get('protocol')}")
            return {
                "success": True,
                "protocol": data.get("protocol"),
                "error": None,
            }

        error_msg = f"Falha na ativação: {response.status_code} {response.text}"
        print(f"[API] {error_msg}")
        return {"success": False, "protocol": None, "error": error_msg}

    except Exception as e:
        error_msg = f"Erro ao ativar plano: {str(e)}"
        print(f"[API] {error_msg}")
        return {"success": False, "protocol": None, "error": error_msg}