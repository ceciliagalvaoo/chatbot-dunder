from typing import List, Dict, Any
from .chatbot_compliance import answer_compliance_question
from .conspiracy_detector import check_conspiracy
from .fraud_detector_simple import run_simple_fraud_check
from .fraud_detector_contextual import run_contextual_fraud_check


# Imprime um título formatado com bordas decorativas
def _print_title(title: str):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80 + "\n")


# Demonstração interativa do chatbot de compliance
def demo_chatbot():
    _print_title("📘 Chatbot de Compliance")
    question = input("Digite sua pergunta sobre a política de compliance:\n> ")
    # Chama o sistema RAG para responder a pergunta
    res = answer_compliance_question(question)
    print("\n--- RESPOSTA ---\n")
    print(res["answer"])
    print("\nEvidências (IDs de trechos usados):", res["evidence_chunks"])


# Demonstração da detecção de conspiração em e-mails
def demo_conspiracy():
    _print_title("🧠 Verificação de Conspiração Michael x Toby")
    # Analisa todos os e-mails em busca de sinais de conspiração
    res = check_conspiracy()
    print("Conspiração detectada?", "SIM" if res["conspiracy"] else "NÃO")
    print("\nJustificativa:")
    print(res["justification"])
    print("\nTrechos de e-mail usados como evidência:")
    for s in res["evidence_snippets"]:
        print(f"- {s}")


# Função auxiliar que imprime transações suspeitas de forma formatada
def _print_suspicious_transactions(results: List[Dict[str, Any]],
                                   key_flag: str,
                                   label: str):
    # Filtra apenas as transações marcadas como suspeitas
    suspicious = [r for r in results if r.get(key_flag)]
    if not suspicious:
        print(f"\nNenhuma transação suspeita encontrada para: {label}.")
        return

    print(f"\n{len(suspicious)} transações suspeitas para: {label}.\n")
    # Imprime detalhes de cada transação suspeita
    for r in suspicious:
        row = r["row"]
        print("-" * 60)
        print("ID:", row.get("id_transacao"))
        print("Data:", row.get("data"))
        print("Funcionário:", row.get("funcionario"), "-", row.get("cargo"))
        print("Descrição:", row.get("descricao"))
        print("Valor:", row.get("valor"), "| Categoria:", row.get("categoria"))
        print("Departamento:", row.get("departamento"))
        print()
        # Imprime justificativa e evidências encontradas
        print("Motivo:", r.get("reason") or r.get("justification"))
        if "policy_evidence" in r:
            print("Regras relevantes:", r["policy_evidence"])
        if "email_evidence" in r:
            print("E-mails relevantes:", r["email_evidence"])
        print()


# Demonstração da detecção de fraudes simples (apenas violações diretas)
def demo_fraud_simple():
    _print_title("💳 Fraudes Simples (sem contexto de e-mails)")
    print("Rodando análise de fraudes em MODO DEMO (primeiras 50 transações)...\n")

    # Executa verificação nas primeiras 40 transações
    results = run_simple_fraud_check(max_rows=40)

    print(f"\n✅ Análise concluída: {len(results)} transações processadas.\n")

    # Exibe transações que violam regras explícitas de compliance
    _print_suspicious_transactions(results, "violation", "quebras diretas de compliance")


# Demonstração da detecção de fraudes contextuais (usando e-mails)
def demo_fraud_contextual():
    _print_title("💼 Fraudes com Contexto de E-mails")
    print("Rodando análise contextual em MODO DEMO (primeiras 40 transações)...\n")

    # Executa verificação contextual nas primeiras 40 transações
    results = run_contextual_fraud_check(max_rows=40)

    print(f"\n✅ Análise concluída: {len(results)} transações processadas.\n")

    # Filtra transações suspeitas baseadas no contexto de e-mails
    suspicious = [r for r in results if r.get("fraud_suspected")]
    if not suspicious:
        print("Nenhuma transação potencialmente fraudulenta encontrada com contexto de e-mails.")
        return

    # Exibe fraudes detectadas através de análise contextual
    _print_suspicious_transactions(suspicious, "fraud_suspected", "fraudes contextuais")


# Loop principal da interface CLI
def main():
    while True:
        # Menu principal com todas as opções disponíveis
        print("\n=== Toby Auditor CLI ===")
        print("1) Chatbot de compliance")
        print("2) Verificar conspiração Michael x Toby")
        print("3) Analisar fraudes simples (regras explícitas)")
        print("4) Analisar fraudes com contexto de e-mails")
        print("0) Sair")
        op = input("\nEscolha uma opção: ").strip()

        # Redireciona para a função correspondente à opção escolhida
        if op == "1":
            demo_chatbot()
        elif op == "2":
            demo_conspiracy()
        elif op == "3":
            demo_fraud_simple()
        elif op == "4":
            demo_fraud_contextual()
        elif op == "0":
            break
        else:
            print("Opção inválida. Tente novamente.")


# Ponto de entrada quando o script é executado diretamente
if __name__ == "__main__":
    main()