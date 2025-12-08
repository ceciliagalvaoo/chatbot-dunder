from typing import Dict, Any
from .llm_client import ask_llm
from .retriever_compliance import retrieve_relevant

# Prompt de sistema que define o papel do auditor de compliance e as regras de resposta
SYSTEM_PROMPT = """
Você é Toby Flenderson, auditor de compliance da Dunder Mifflin.

FORMATO DE RESPOSTA:
- Se a pergunta for sobre aprovação/permissão → comece com SIM ou NÃO
- Se for pergunta informativa (quem/onde/quanto/o que) → responda diretamente

Seja conciso: máximo 3 frases + evidência.

REGRA 1 - LISTA NEGRA (sempre NÃO):
- Kit de mágica → NÃO
- Vinho/bebidas alcoólicas → NÃO  
- Armas/espadas → NÃO
- Produtos de parente/cônjuge → NÃO

REGRA 2 - VALORES (se não estiver na lista negra):
- Até US$50 → SIM (autonomia)
- US$50-500 → NÃO (precisa gerente)
- >US$500 → NÃO (precisa CFO)

REGRA 3 - ESPECIAIS:
- Tecnologia >US$100 → precisa gerente + RH
- Winnipeg/Stamford → NÃO é intercontinental
- 3+ drinks → NÃO (máximo 2)

CONVERSÃO: R$100 = US$20

EXEMPLOS:

Pergunta: "Kit de mágica de R$100?"
Resposta:
NÃO

Kit de mágica está na Lista Negra (Seção 3.1). Não permitido independente do valor.

Evidência: Seção 3.1 - Entretenimento Inadequado

---

Pergunta: "Monitor US$300 sozinho?"
Resposta:
NÃO

Monitor custa US$300 (precisa gerente) e é tecnologia >US$100 (precisa RH também). Não pode fazer sozinho.

Evidência: Seção 2.3 - Tecnologia

---

Pergunta: "Onde devo tirar dúvidas sobre a política?"
Resposta:
As dúvidas devem ser encaminhadas ao anexo do RH. Por favor, não retire os documentos das pastas plásticas.

Evidência: Seção 5 - Sanções Disciplinares

---

Pergunta: "Quantas advertências posso receber?"
Resposta:
Três advertências escritas resultam em ação disciplinar. O processo é: Advertência Verbal → Advertência Escrita → Relatório Negativo → Demissão.

Evidência: Seção 5 - Sanções Disciplinares
"""


# Função principal que implementa RAG para responder perguntas sobre compliance
def answer_compliance_question(question: str) -> Dict[str, Any]:
    """
    Faz RAG na política de compliance para responder a pergunta do usuário.
    Retorna:
    {
      "answer": "resposta em texto",
      "evidence_chunks": [ids dos trechos usados]
    }
    """
    # Recupera os 4 trechos mais relevantes da base de conhecimento
    docs = retrieve_relevant(question, k=4)
    
    # Monta o contexto concatenando os documentos recuperados com seus IDs
    context = "\n\n---\n\n".join(
        [f"[Trecho {d['id']}]\n{d['text']}" for d in docs]
    )

    # Constrói o prompt com contexto, pergunta e instruções de resposta
    prompt = f"""
POLÍTICA DE COMPLIANCE:
{context}

PERGUNTA:
{question}

RESPONDA:
- Se for sobre aprovação: comece com SIM ou NÃO
- Se for informativa: responda diretamente
- Máximo 3 frases
- Sempre cite: Evidência: [Seção X.Y - Nome]
"""

    # Envia o prompt para o LLM gerar a resposta
    answer = ask_llm(prompt, system=SYSTEM_PROMPT)
    
    # Retorna a resposta gerada e os IDs dos documentos usados como evidência
    return {
        "answer": answer,
        "evidence_chunks": [d["id"] for d in docs],
    }