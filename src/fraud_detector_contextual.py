import csv
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from .llm_client import llm_json
from .retriever_compliance import retrieve_relevant

# Define os caminhos base do projeto e localização dos arquivos de dados
ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"

TRANS_PATH = DATA_DIR / "transacoes_bancarias.csv"
EMAILS_PATH = DATA_DIR / "emails_internos.txt"

# Prompt de sistema que define o papel do auditor de fraudes contextual
SYSTEM_PROMPT = """
Você é um auditor de fraudes da Dunder Mifflin.

Algumas transações só são fraudulentas quando analisamos o CONTEXTO,
especialmente conversas em e-mails (combinando desvios, maquiando gastos, etc.).

Considere:
- as regras de compliance fornecidas,
- os detalhes da transação,
- os trechos de e-mails relacionados (quando existirem).

Se os e-mails sugerirem intenção de fraude, conluio, desvio de verba ou
maquiagem de despesas, marque "fraud_suspected": true.
"""


# Carrega todas as transações do arquivo CSV
def _load_transactions() -> List[Dict[str, Any]]:
    if not TRANS_PATH.exists():
        raise FileNotFoundError(f"Arquivo de transações não encontrado: {TRANS_PATH}")
    with TRANS_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [dict(r) for r in reader]
    return rows


# Carrega o conteúdo bruto do arquivo de e-mails internos
def _load_emails_raw() -> str:
    if not EMAILS_PATH.exists():
        raise FileNotFoundError(f"Arquivo de e-mails não encontrado: {EMAILS_PATH}")
    return EMAILS_PATH.read_text(encoding="utf-8")


# Busca e-mails que mencionam o funcionário, valor ou descrição da transação
def find_related_emails(employee_name: str, amount: str, description: str = "") -> str:
    """
    Busca por nome do funcionário, valor ou palavras-chave da descrição.
    Útil para detectar fraudes contextuais onde itens são mencionados nos e-mails.
    """
    raw = _load_emails_raw()
    lines = raw.splitlines()

    matches: List[str] = []
    name_lower = (employee_name or "").lower()
    amount_str = str(amount).strip()
    
    # Extrai palavras-chave da descrição (ex: "Walkie Talkies" → ["walkie", "talkies"])
    desc_keywords = []
    if description:
        # Remove palavras comuns e pega só as relevantes
        stop_words = {"de", "do", "da", "para", "com", "despesa", "compra", "gasto"}
        words = description.lower().replace("-", " ").split()
        desc_keywords = [w for w in words if len(w) > 3 and w not in stop_words]

    # Procura linha por linha
    for ln in lines:
        ln_lower = ln.lower()
        
        # Busca por nome do funcionário
        if name_lower and name_lower in ln_lower:
            matches.append(ln)
        # Busca por valor exato
        elif amount_str and amount_str in ln:
            matches.append(ln)
        # Busca por palavras-chave da descrição (mais flexível)
        elif desc_keywords:
            for keyword in desc_keywords:
                if keyword in ln_lower:
                    matches.append(ln)
                    break  # Não duplicar a mesma linha

    # Limita para não explodir o contexto do LLM
    if len(matches) > 80:
        matches = matches[:80]

    return "\n".join(matches)


# Analisa uma transação individual considerando contexto de e-mails e compliance
def check_transaction_with_context(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analisa UMA transação considerando contextos de e-mail.
    Retorna:
    {
      "row": {...},
      "fraud_suspected": bool,
      "justification": "...",
      "email_evidence": ["...", "..."],
      "policy_evidence": ["...", "..."]
    }
    """
    # Extrai informações da transação
    employee = row.get("funcionario", "") or row.get("employee", "")
    amount = row.get("valor", "") or row.get("amount", "")
    description = row.get("descricao", "") or row.get("description", "")

    # Busca e-mails relacionados a esta transação (nome, valor OU descrição)
    emails_context = find_related_emails(employee, str(amount), description)

    # Se não há e-mails relacionados, marca como não suspeito
    if not emails_context.strip():
        return {
            "row": row,
            "fraud_suspected": False,
            "justification": "Nenhum e-mail relacionado foi encontrado para esta transação.",
            "email_evidence": [],
            "policy_evidence": [],
        }

    # Recupera trechos relevantes da política de compliance
    policy_docs = retrieve_relevant(
        f"{row.get('descricao', '')} {row.get('categoria', '')} {amount}",
        k=2,
    )
    policy_context = "\n\n---\n\n".join(d["text"] for d in policy_docs)

    # Constrói o prompt com todos os contextos: compliance, transação e e-mails
    user_prompt = f"""
REGRAS DE COMPLIANCE (trechos relevantes):
{policy_context}

TRANSACAO:
{row}

TRECHOS DE E-MAILS RELACIONADOS (se houver):
\"\"\" 
{emails_context}
\"\"\"


