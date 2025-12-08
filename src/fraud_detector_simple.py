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

