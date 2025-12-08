import csv
from pathlib import Path
from typing import Dict, Any, List, Optional
from .llm_client import llm_json
from .retriever_compliance import retrieve_relevant

# Define os caminhos base do projeto e localização dos arquivos de dados
ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"

TRANS_PATH = DATA_DIR / "transacoes_bancarias.csv"

# Prompt de sistema que define o papel do auditor e critérios de análise
SYSTEM_PROMPT = """
Você é um auditor financeiro e de compliance da Dunder Mifflin.

TAREFA:
- Avaliar se uma transação bancária isolada viola a política de compliance,
  considerando os trechos fornecidos.
- Focar em:
  - valores acima do limite sem aprovação,
  - categorias proibidas (ex.: entretenimento pessoal, jogos, etc.),
  - itens explicitamente listados como "lista negra" no manual,
  - reembolsos em moeda estrangeira sem justificativa, etc.

IMPORTANTE:
- Não invente regras que não estão presentes nos trechos da política.
- Se não houver regra clara aplicável, marque "violation": false.
"""


# Carrega todas as transações do arquivo CSV
def _load_transactions() -> List[Dict[str, Any]]:
    if not TRANS_PATH.exists():
        raise FileNotFoundError(f"Arquivo de transações não encontrado: {TRANS_PATH}")
    with TRANS_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [dict(r) for r in reader]
    return rows


# Analisa uma transação individual contra a política de compliance
def check_transaction_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analisa UMA linha de transação e retorna:
    {
      "row": {...},
      "violation": bool,
      "reason": "...",
      "policy_evidence": ["...", "..."]
    }
    """
    # Recupera os 3 trechos mais relevantes da política usando RAG
    docs = retrieve_relevant(
        f"{row.get('descricao', '')} {row.get('categoria', '')} {row.get('valor', '')}",
        k=3,
    )
    policy_context = "\n\n---\n\n".join(d["text"] for d in docs)

    # Constrói o prompt com a política recuperada e a transação a analisar
    user_prompt = f"""
POLÍTICA DE COMPLIANCE (trechos relevantes):
{policy_context}

TRANSACAO PARA ANALISE (dados brutos):
{row}

Pergunta:
Esta transação, isoladamente, viola alguma regra explícita da política de compliance?

Responda EM JSON, no formato:

{{
  "violation": true/false,
  "reason": "explique em 1-2 frases, citando a regra aplicada ou dizendo que não há regra clara",
  "policy_evidence": [
    "citação ou resumo de regra relevante 1",
    "regra relevante 2"
  ]
}}
"""

    # Envia para o LLM e recebe análise estruturada em JSON
    result = llm_json(user_prompt, system=SYSTEM_PROMPT)

    # Retorna resultado estruturado com violação detectada e evidências
    return {
        "row": row,
        "violation": bool(result.get("violation", False)),
        "reason": result.get("reason", ""),
        "policy_evidence": result.get("policy_evidence", []),
    }


