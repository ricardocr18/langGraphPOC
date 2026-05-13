"""
Documento de conhecimento TIM para o RAG.
Em produção, este conteúdo viria de um sistema externo (Confluence, SharePoint etc).
Aqui criamos manualmente para fins de aprendizado.
"""

TIM_KNOWLEDGE_BASE = """
# Catálogo de Planos TIM — Base de Conhecimento Agente

## Planos Pré-Pago

### TIM Pré Top
- Preço: R$ 15,00/recarga mínima
- Internet: 1GB por recarga
- Ligações: ilimitadas para TIM, 30 min para outras operadoras
- Validade: 7 dias
- Elegibilidade: todos os clientes pré-pago ativos há menos de 6 meses

### TIM Pré Ultra
- Preço: R$ 25,00/recarga mínima
- Internet: 3GB por recarga + 1GB bônus para redes sociais
- Ligações: ilimitadas para TIM e outras operadoras
- Validade: 15 dias
- Elegibilidade: clientes pré-pago com histórico de recarga regular

## Planos Controle

### TIM Controle 30
- Preço: R$ 30,00/mês
- Internet: 10GB + 5GB bônus streaming (Netflix, Prime Video)
- Ligações: ilimitadas para qualquer operadora
- SMS: 100 mensagens/mês
- Elegibilidade: clientes novos ou migrando do pré-pago

### TIM Controle 50
- Preço: R$ 50,00/mês
- Internet: 20GB + streaming ilimitado TIM Music + Disney+
- Ligações: ilimitadas
- Roaming nacional: incluso
- Elegibilidade: clientes com CPF com score mínimo 500 no Crivo

## Planos Pós-Pago

### TIM Black 70
- Preço: R$ 70,00/mês
- Internet: 40GB + dados ilimitados no WhatsApp
- Ligações: ilimitadas nacional e internacional (EUA, Portugal)
- Apps inclusos: HBO Max, Disney+, Paramount+
- Elegibilidade: clientes com score Crivo acima de 700

### TIM Black 100
- Preço: R$ 100,00/mês
- Internet: ilimitada
- Ligações: ilimitadas global (60 países)
- Roaming internacional incluso
- Apps premium inclusos
- Elegibilidade: clientes com histórico de pagamento excelente

## Processo de Ativação

### Fluxo padrão de ativação
1. Identificar cliente via CPF ou número de telefone
2. Consultar elegibilidade na API (campo: is_eligible)
3. Apresentar planos elegíveis com argumentação personalizada
4. Aguardar aceite do cliente (tentativas: máximo 3)
5. Postar ordem de ativação no sistema
6. Enviar SMS de confirmação ao cliente
7. Registrar atendimento com resultado ATIVACAO

### Motivos comuns de inelegibilidade
- Débito em aberto: cliente possui fatura vencida
- Score insuficiente: Crivo abaixo do mínimo do plano
- Plano bloqueado: cliente solicitou bloqueio de upgrade
- Portabilidade pendente: processo em andamento

### Argumentação de vendas
- Destaque sempre o benefício principal do plano (internet, streaming, roaming)
- Para clientes pré-pago migrando: enfatize economia e comodidade do débito automático
- Para clientes resistentes: ofereça período de trial de 7 dias (quando disponível)
- Limite de tentativas de negociação: 3 por atendimento

## Transferência para Atendimento Humano (ATH)
- Acionar quando: cliente insiste após 3 negativas, reclamação de serviço, solicitação explícita
- Protocolo: gerar código de protocolo e informar ao cliente antes de transferir
- Registro obrigatório: mesmo com transferência, registrar o atendimento como INFORMACAO
"""

def get_knowledge_documents() -> list[str]:
    """Retorna o conhecimento dividido em chunks para indexação."""
    chunks = []
    current_chunk = ""

    for line in TIM_KNOWLEDGE_BASE.strip().split("\n"):
        # Novo chunk a cada seção de nível 2 (##)
        if line.startswith("## ") and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = line + "\n"
        else:
            current_chunk += line + "\n"

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks