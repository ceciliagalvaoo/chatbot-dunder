import json
import os
from pathlib import Path
from typing import List, Dict, Any

import numpy as np

from .llm_client import embed_text, file_sha1

# Define os caminhos base e localização dos arquivos de dados
ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"

POLICY_PATH = DATA_DIR / "politica_compliance.txt"
INDEX_PATH = DATA_DIR / "compliance_index.json"


# Carrega o texto completo da política de compliance
def _load_policy_text() -> str:
    if not POLICY_PATH.exists():
        raise FileNotFoundError(f"Arquivo de política não encontrado: {POLICY_PATH}")
    return POLICY_PATH.read_text(encoding="utf-8")


# Divide o texto da política em chunks menores, respeitando parágrafos
def _chunk_policy(chunk_size: int = 1000) -> List[Dict[str, Any]]:
    """
    Quebra o texto em blocos ~chunk_size chars, respeitando parágrafos.
    """
    text = _load_policy_text()
    # Separa o texto em parágrafos (blocos separados por linha dupla)
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: List[str] = []
    current = ""

    # Agrupa parágrafos em chunks sem ultrapassar o tamanho limite
    for p in paragraphs:
        if len(current) + len(p) + 2 <= chunk_size:
            current += ("\n\n" if current else "") + p
        else:
            if current:
                chunks.append(current)
            current = p
    if current:
        chunks.append(current)

    # Retorna lista de dicionários com ID e texto de cada chunk
    return [{"id": i, "text": c} for i, c in enumerate(chunks)]


# Constrói ou reconstrói o índice de embeddings da política
def build_index(force: bool = False) -> None:
    """
    Gera (ou regenera) o índice de embeddings da política de compliance.
    Salva em JSON:
      - chunks (id, text, embedding)
      - source_sha1 (para saber se o arquivo mudou).
    """
    # Verifica se precisa reconstruir o índice
    if not force and INDEX_PATH.exists():
        # Só reconstrói se o hash do arquivo de política tiver mudado
        existing = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
        old_sha = existing.get("_meta", {}).get("source_sha1")
        if old_sha == file_sha1(str(POLICY_PATH)):
            return  # índice já está atualizado

    # Divide a política em chunks
    chunks = _chunk_policy()
    
    # Gera embedding para cada chunk
    for c in chunks:
        c["embedding"] = embed_text(c["text"])

    # Monta estrutura de dados com metadados e chunks
    data = {
        "_meta": {
            "source_sha1": file_sha1(str(POLICY_PATH)),
            "num_chunks": len(chunks),
        },
        "chunks": chunks,
    }
    
    # Salva o índice em arquivo JSON
    INDEX_PATH.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


# Carrega o índice do disco e converte embeddings para numpy arrays
def _load_index() -> Dict[str, Any]:
    # Garante que o índice existe antes de carregar
    if not INDEX_PATH.exists():
        build_index(force=True)
    data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    
    # Converte embeddings de lista para numpy array para cálculos eficientes
    for c in data["chunks"]:
        c["embedding"] = np.array(c["embedding"], dtype=float)
    return data


# Função principal de recuperação: busca os k chunks mais relevantes para a query
def retrieve_relevant(query: str, k: int = 4) -> List[Dict[str, Any]]:
    """
    Retorna os k chunks mais similares à query, usando similaridade de cosseno.
    """
    # Garante que o índice está atualizado
    build_index(force=False)
    idx = _load_index()
    chunks = idx["chunks"]

    # Gera embedding da query
    q_emb = np.array(embed_text(query), dtype=float)

    # Calcula similaridade de cosseno entre dois vetores
    def cos_sim(a, b):
        denom = float(np.linalg.norm(a) * np.linalg.norm(b))
        return float(a @ b / denom) if denom != 0 else 0.0

    # Calcula similaridade entre query e cada chunk
    scored = [
        (cos_sim(q_emb, c["embedding"]), c)
        for c in chunks
    ]
    
    # Ordena por similaridade (maior primeiro) e retorna top k
    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:k]]