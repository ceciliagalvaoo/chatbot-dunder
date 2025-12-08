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


