import os
from pathlib import Path
from typing import Dict, Any, List
from .llm_client import llm_json

# Define os caminhos base do projeto e localização dos arquivos de dados
ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
EMAILS_PATH = DATA_DIR / "emails_internos.txt"

# Prompt de sistema que define o papel do auditor investigativo
SYSTEM_PROMPT = """
Você é um auditor investigativo.
Sua tarefa é descobrir se Michael Scott está conspirando contra Toby Flenderson.
Conspiração significa: intenção clara de prejudicar, sabotar, humilhar ou manipular.
Responda sempre em JSON.
"""

# Carrega o conteúdo do arquivo de e-mails internos
def _load_emails_text() -> str:
    return EMAILS_PATH.read_text(encoding="utf-8")


# Divide o texto em blocos menores para evitar estouro de tokens no LLM
def _chunk_text(text: str, max_chars=2500) -> List[str]:
    """
    Divide o texto em blocos menores para evitar estouro de tokens.
    """
    parts = []
    while len(text) > max_chars:
        cut = text[:max_chars]
        parts.append(cut)
        text = text[max_chars:]
    if text:
        parts.append(text)
    return parts


# Analisa todos os e-mails em blocos e agrega evidências de conspiração
def check_conspiracy() -> Dict[str, Any]:
    """
    Analisa blocos de e-mails e agrega sinais de conspiração.
    """
    # Carrega o texto completo dos e-mails
    raw = _load_emails_text()
    
    # Divide em chunks de até 2500 caracteres
    chunks = _chunk_text(raw, max_chars=2500)

    # Lista para acumular evidências encontradas
    evidence = []
    # Flag que indica se houve conspiração detectada
    conspiracy_flag = False

    # Processa cada chunk individualmente
    for i, chunk in enumerate(chunks):
        # Constrói o prompt para análise deste bloco específico
        prompt = f"""
Trecho de e-mails internos (parte {i+1}/{len(chunks)}):
\"\"\" 
{chunk}
\"\"\"

Pergunta:
Existe evidência de conspiração de Michael Scott contra Toby Flenderson neste bloco?

Responda estritamente em JSON no formato:
{{
  "conspiracy": true/false,
  "justification": "explicação curta",
  "evidence_snippets": ["trecho1", "trecho2"]
}}
"""
        # Envia o prompt para o LLM e recebe resposta em JSON
        res = llm_json(prompt, system=SYSTEM_PROMPT)

        # Se o bloco contém conspiração, marca a flag e adiciona as evidências
        if res.get("conspiracy"):
            conspiracy_flag = True
            evidence.extend(res.get("evidence_snippets", []))

    # Retorna resultado agregado de todos os blocos analisados
    return {
        "conspiracy": conspiracy_flag,
        "justification": "Foram encontrados indícios em blocos analisados."
                         if conspiracy_flag else
                         "Nenhum bloco apresentou sinais de conspiração.",
        "evidence_snippets": evidence,
    }