import os
import json
import hashlib
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from groq import Groq
import time

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Lê a chave da API e o modelo a ser usado do ambiente
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

# Valida se a chave da API foi configurada
if not GROQ_API_KEY:
    raise RuntimeError("Defina GROQ_API_KEY no arquivo .env")

# Inicializa o cliente da Groq com a chave da API
client = Groq(api_key=GROQ_API_KEY)

print(f"✅ API Key carregada. Modelo: {GROQ_MODEL}")


# Função que chama o LLM e retorna resposta em texto simples
def ask_llm(prompt: str, system: Optional[str] = None) -> str:
    # Delay para evitar rate limiting da API
    time.sleep(0.7)
    """
    Retorna uma resposta em texto simples usando o modelo da Groq.
    """
    messages = []
    # Adiciona mensagem de sistema se fornecida
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    # Chama a API da Groq com os parâmetros configurados
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.2,
        max_completion_tokens=500,
    )

    # Extrai e retorna o conteúdo da resposta
    return response.choices[0].message.content


# Função auxiliar que limpa e extrai JSON de texto potencialmente mal formatado
def clean_json(txt: str) -> dict:
    """
    Tenta fazer parse de JSON de forma robusta:
    1) Primeiro tenta json.loads direto.
    2) Se falhar, tenta extrair o PRIMEIRO objeto JSON bem balanceado
       (contando chaves '{' e '}') e faz json.loads só nesse pedaço.
    """
    txt = (txt or "").strip()
    
    # Tentativa 1: parse direto do texto
    try:
        return json.loads(txt)
    except Exception:
        pass

    # Tentativa 2: extrair primeiro objeto JSON válido do texto
    start = txt.find("{")
    if start == -1:
        raise ValueError("Falha ao interpretar JSON: nenhum '{' encontrado.")

    # Conta abertura e fechamento de chaves para encontrar objeto completo
    depth = 0
    end = None
    for i, ch in enumerate(txt[start:], start=start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i
                break

    # Tenta fazer parse do objeto JSON extraído
    if end is not None:
        candidate = txt[start : end + 1]
        try:
            return json.loads(candidate)
        except Exception as e:
            raise ValueError(f"Falha ao interpretar JSON (mesmo após recorte): {e}\nTexto: {candidate}") from e

    raise ValueError("Falha ao interpretar JSON: não foi possível fechar as chaves.")


# Função que chama o LLM e força resposta em formato JSON estruturado
def llm_json(prompt: str, system: Optional[str] = None) -> dict:
    # Delay para evitar rate limiting da API
    time.sleep(0.7)
    messages = []
    
    # Adiciona mensagem de sistema se fornecida
    if system:
        messages.append({"role": "system", "content": system})

    # Adiciona instruções explícitas para garantir JSON válido
    messages.append({
        "role": "user",
        "content": (
            prompt
            + "\n\nResponda ESTRITAMENTE em JSON válido. "
              "NÃO inclua texto fora do JSON. "
              "NÃO use comentários. "
              "NÃO coloque vírgula sobrando no fim de listas ou objetos. "
              "Sua resposta será lida com json.loads em Python."
        ),
    })

    # Chama a API com temperatura 0 para respostas mais determinísticas
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.0,
        max_completion_tokens=800,
    )

    txt = (response.choices[0].message.content or "").strip()

    # Tenta fazer parse do JSON com tratamento de erro robusto
    try:
        return clean_json(txt)
    except Exception as e:
        # Em caso de falha, loga o erro mas não quebra o fluxo
        print("\n⚠️ Falha ao interpretar JSON do modelo:", e)
        print("🔎 Resposta bruta foi:\n", txt[:1000], "...\n")
        return {}


# Gera embeddings simples usando hash local (sem dependências externas)
def embed_text(text: str) -> List[float]:
    """
    Embedding leve, determinístico e 100% local.
    NÃO depende de downloads, NÃO trava, NÃO usa GPU.
    Suficiente para RAG pequeno (como política de compliance).
    """
    # Tokeniza o texto de forma simples
    tokens = text.lower().split()
    dim = 256  # dimensão do vetor de embedding
    vec = [0.0] * dim

    # Para cada token, usa hash para mapear em uma posição do vetor
    for tok in tokens:
        h = int(hashlib.sha1(tok.encode("utf-8")).hexdigest(), 16)
        idx = h % dim
        vec[idx] += 1.0

    return vec


# Calcula SHA-1 de um arquivo para detectar mudanças
def file_sha1(path: str) -> str:
    """
    Retorna SHA-1 de um arquivo. Usado para detectar se a política mudou.
    """
    h = hashlib.sha1()
    # Lê o arquivo em chunks para não sobrecarregar memória
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()