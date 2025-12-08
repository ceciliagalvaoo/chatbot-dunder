import os
import pandas as pd
import streamlit as st
from datetime import datetime

from src.chatbot_compliance import answer_compliance_question
from src.conspiracy_detector import check_conspiracy
from src.fraud_detector_simple import run_simple_fraud_check
from src.fraud_detector_contextual import run_contextual_fraud_check

# Define o caminho para os dados
DATA_DIR = "data"
TRANS_PATH = os.path.join(DATA_DIR, "transacoes_bancarias.csv")


# Carrega as transações do CSV e armazena em cache do Streamlit
@st.cache_data
def load_transactions() -> pd.DataFrame:
    df = pd.read_csv(TRANS_PATH)
    df.columns = [c.strip().lower() for c in df.columns]
    return df


# Executa verificação simples de fraudes com cache (evita reprocessamento)
@st.cache_data
def run_simple_fraud_cached(max_rows: int):
    return run_simple_fraud_check(max_rows=max_rows)


# Executa verificação contextual de fraudes com cache
@st.cache_data
def run_contextual_fraud_cached(max_rows: int):
    return run_contextual_fraud_check(max_rows=max_rows)


# Injeta CSS customizado para melhorar a aparência visual da interface
def inject_custom_css():
    st.markdown("""
    <style>
    /* Melhorar cards */
    .stAlert {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    
    /* Melhorar métricas */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }
    
    /* Badges customizados */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    .badge-danger {
        background-color: #ff4b4b;
        color: white;
    }
    
    .badge-success {
        background-color: #00cc66;
        color: white;
    }
    
    .badge-warning {
        background-color: #ffa500;
        color: white;
    }
    
    .badge-info {
        background-color: #0ea5e9;
        color: white;
    }
    
    /* Card customizado */
    .custom-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #0ea5e9;
        margin: 1rem 0;
    }
    
    /* Títulos melhorados */
    .section-title {
        color: #0ea5e9;
        font-size: 1.25rem;
        font-weight: 700;
        margin: 1.5rem 0 0.5rem 0;
        border-bottom: 2px solid #0ea5e9;
        padding-bottom: 0.5rem;
    }
    
    /* Highlight de evidências */
    .evidence-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
    }
    
    /* Melhorar tabelas */
    .dataframe {
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)


# Configura o layout geral da página Streamlit
st.set_page_config(
    page_title="Toby Auditor - Dunder Mifflin",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Aplica os estilos CSS customizados
inject_custom_css()

# Header principal da aplicação
st.title("Toby Auditor - Dunder Mifflin")
st.caption("Sistema Inteligente de Auditoria e Compliance | Scranton Branch")

st.markdown("---")

# Cards de apresentação dos principais módulos
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div class="custom-card">
        <h3>Chatbot RAG</h3>
        <p>Consulte a política de compliance com respostas baseadas em evidências</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="custom-card">
        <h3>Detector de Conspiração</h3>
        <p>Analisa e-mails para identificar planos suspeitos</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="custom-card">
        <h3>Detector de Fraudes</h3>
        <p>Identifica violações diretas e contextuais</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Sidebar com configurações e estatísticas do sistema
with st.sidebar:
    st.header("Configuração do Sistema")
    groq_model = os.getenv("GROQ_MODEL", "não definido")
    
    st.markdown(f"""
    **Modelo LLM:** `{groq_model}`  
    **Status:** <span class="badge badge-success">Operacional</span>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Exibe estatísticas do dataset de transações
    st.subheader("Estatísticas")
    try:
        df_stats = load_transactions()
        st.metric("Total de Transações", len(df_stats))
        st.metric("Valor Total", f"R$ {df_stats['valor'].sum():,.2f}")
        st.metric("Funcionários", df_stats['funcionario'].nunique())
    except Exception as e:
        st.error("Erro ao carregar estatísticas")
    
    st.markdown("---")
    st.caption("**Dica:** Modos demo limitam transações para otimizar uso de tokens")
    st.caption(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# Cria as abas principais da interface
tabs = st.tabs(
    [
        "Chatbot de Compliance",
        "Conspiração Michael x Toby",
        "Fraudes (regras explícitas)",
        "Fraudes (com contexto de e-mails)",
    ]
)

# Tab 1: Chatbot de Compliance usando RAG
with tabs[0]:
    st.markdown('<h2 class="section-title">Consulta à Política de Compliance</h2>', unsafe_allow_html=True)

    # Info box explicando o funcionamento
    st.info("""
    **Como funciona:** Faça perguntas sobre reembolsos, alçadas de aprovação, itens proibidos, 
    lista negra, limites, etc. O sistema usa **RAG (Retrieval-Augmented Generation)** para buscar 
    trechos relevantes da política e gerar respostas precisas.
    """)

    # Campo de entrada para a pergunta do usuário
    question = st.text_area(
        "Digite sua dúvida sobre compliance:",
        placeholder="Ex: Posso reembolsar uma compra de US$ 80 em 'Material de Escritório' sem aprovação do Michael?",
        height=120,
    )

    # Botões de ação
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        ask_button = st.button("Perguntar ao TobyBot", type="primary", use_container_width=True)
    with col2:
        if st.button("Limpar", use_container_width=True):
            st.rerun()

    # Processa a pergunta quando o botão é clicado
    if ask_button:
        if not question.strip():
            st.warning("Por favor, escreva uma pergunta primeiro.")
        else:
            with st.spinner("Consultando a política de compliance..."):
                try:
                    # Chama o sistema RAG para responder
                    result = answer_compliance_question(question)

                    # Exibe a resposta do chatbot
                    st.markdown('<div class="section-title">Resposta do TobyBot</div>', unsafe_allow_html=True)
                    st.success(result["answer"])

                    # Mostra as evidências utilizadas (chunks da política)
                    st.markdown('<div class="section-title">Evidências Utilizadas</div>', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"""
                        <div class="evidence-box">
                        <strong>Trechos da política consultados:</strong> {', '.join([f'Chunk #{id}' for id in result["evidence_chunks"]])}
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.metric("Trechos usados", len(result["evidence_chunks"]))
                    
                    # Opção para exportar a resposta
                    with st.expander("Exportar resposta"):
                        export_text = f"""
PERGUNTA: {question}

RESPOSTA:
{result["answer"]}

EVIDÊNCIAS: {', '.join([f'Chunk #{id}' for id in result["evidence_chunks"]])}

Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}
                        """
                        st.download_button(
                            "Baixar como TXT",
                            export_text,
                            file_name=f"resposta_compliance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
                
                except Exception as e:
                    st.error(f"Erro ao processar pergunta: {str(e)}")
                    with st.expander("Detalhes do erro"):
                        st.exception(e)


# Tab 2: Detector de Conspiração
with tabs[1]:
    st.markdown('<h2 class="section-title">Detector de Conspiração Michael x Toby</h2>', unsafe_allow_html=True)

    st.info("""
    **Objetivo:** Analisar o dump completo de e-mails internos da Dunder Mifflin para 
    identificar evidências de que Michael Scott está conspirando contra Toby Flenderson 
    (Operação Fênix, planos secretos, sabotagem, etc.).
    """)

    col1, col2 = st.columns([2, 1])
    with col1:
        analyze_button = st.button("Iniciar Análise de Conspiração", type="primary", use_container_width=True)
    
    # Executa a análise quando o botão é clicado
    if analyze_button:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("Carregando e-mails internos...")
        progress_bar.progress(25)
        
        with st.spinner("Analisando padrões de conspiração nos e-mails..."):
            try:
                progress_bar.progress(50)
                # Chama o detector de conspiração
                res = check_conspiracy()
                progress_bar.progress(100)
                status_text.empty()

                conspiracy = res.get("conspiracy", False)
                justification = res.get("justification", "")
                snippets = res.get("evidence_snippets", [])

                # Exibe o resultado de forma visual destacada
                st.markdown("---")
                
                if conspiracy:
                    st.markdown("""
                    <div style="background-color: #ff4b4b; padding: 1.5rem; border-radius: 0.5rem; color: white;">
                        <h2>ALERTA: Conspiração Detectada!</h2>
                        <p>O sistema identificou indícios de conspiração contra Toby Flenderson.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="background-color: #00cc66; padding: 1.5rem; border-radius: 0.5rem; color: white;">
                        <h2>Nenhuma Conspiração Detectada</h2>
                        <p>Não foram encontrados indícios fortes de conspiração nos e-mails analisados.</p>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("---")
                
                # Métricas resumidas
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Status", "Conspiração" if conspiracy else "Limpo")
                with col2:
                    st.metric("Evidências Encontradas", len(snippets))
                with col3:
                    risk_level = "ALTO" if conspiracy else "BAIXO"
                    st.metric("Nível de Risco", risk_level)

                # Justificativa detalhada
                st.markdown('<div class="section-title">Análise Detalhada</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="custom-card">
                    <strong>Justificativa:</strong><br>
                    {justification or "_Sem justificativa detalhada._"}
                </div>
                """, unsafe_allow_html=True)

                # Exibe trechos de e-mails suspeitos
                if snippets:
                    st.markdown('<div class="section-title">Trechos de E-mails Suspeitos</div>', unsafe_allow_html=True)
                    for i, s in enumerate(snippets, 1):
                        st.markdown(f"""
                        <div class="evidence-box">
                            <strong>Evidência #{i}:</strong><br>
                            <em>"{s}"</em>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Opção para exportar relatório completo
                    with st.expander("Exportar Relatório"):
                        report_text = f"""
RELATÓRIO DE ANÁLISE DE CONSPIRAÇÃO
Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}

STATUS: {"CONSPIRAÇÃO DETECTADA" if conspiracy else "NENHUMA CONSPIRAÇÃO"}

JUSTIFICATIVA:
{justification}

EVIDÊNCIAS ENCONTRADAS ({len(snippets)}):
{"".join([f"\\n{i}. {s}" for i, s in enumerate(snippets, 1)])}
                        """
                        st.download_button(
                            "Baixar Relatório Completo",
                            report_text,
                            file_name=f"relatorio_conspiracao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
                else:
                    st.caption("Nenhum trecho específico foi retornado como evidência.")
            
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"❌ Erro durante a análise: {str(e)}")
                with st.expander("🔍 Detalhes do erro"):
                    st.exception(e)


# Tab 3: Detecção de fraudes simples (violações diretas)
with tabs[2]:
    st.markdown('<h2 class="section-title">Detecção de Quebras Diretas de Compliance</h2>', unsafe_allow_html=True)

    st.info("""
    **Método:** Análise individual de transações bancárias verificando violações **diretas** 
    da política de compliance (valores acima da alçada, categorias proibidas, lista negra, etc.) 
    sem necessidade de contexto de e-mails.
    """)

    df = load_transactions()
    
    # Preview dos dados de transações
    with st.expander("Visualizar Transações Bancárias"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de Registros", len(df))
        with col2:
            st.metric("Valor Total", f"R$ {df['valor'].sum():,.2f}")
        with col3:
            st.metric("Categorias", df['categoria'].nunique())
        with col4:
            st.metric("Período", f"{df['data'].min()} a {df['data'].max()}" if 'data' in df.columns else "N/A")
        
        st.dataframe(df, use_container_width=True, height=300)

    st.markdown("---")
    
    # Controles de configuração da análise
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### Configuração da Análise")
        max_rows_simple = st.slider(
            "Número de transações a analisar",
            min_value=5,
            max_value=min(200, len(df)),
            value=20,
            step=5,
            help="Limita análise para otimizar uso de tokens da API",
        )
    
    with col2:
        st.markdown("### Escopo")
        st.metric("Transações selecionadas", max_rows_simple)
        percentage = (max_rows_simple / len(df)) * 100
        st.progress(percentage / 100)
        st.caption(f"{percentage:.1f}% do total")

    # Executa a análise de fraudes simples
    if st.button("Iniciar Análise de Fraudes Simples", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text(f"Analisando {max_rows_simple} transações...")
        progress_bar.progress(20)
        
        with st.spinner("Verificando violações de compliance..."):
            try:
                # Executa a análise usando a função cacheada
                results = run_simple_fraud_cached(max_rows=max_rows_simple)
                progress_bar.progress(100)
                status_text.empty()

                # Filtra apenas transações com violação
                suspicious = [r for r in results if r.get("violation")]

                # Exibe resumo em cards visuais
                st.markdown("---")
                st.markdown('<div class="section-title">Resultado da Análise</div>', unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Analisadas", len(results), delta=None)
                with col2:
                    violation_count = len(suspicious)
                    st.metric("Violações", violation_count, delta=f"-{violation_count}" if violation_count > 0 else "0")
                with col3:
                    compliance_rate = ((len(results) - len(suspicious)) / len(results) * 100) if results else 0
                    st.metric("Taxa de Compliance", f"{compliance_rate:.1f}%")
                with col4:
                    risk_level = "ALTO" if len(suspicious) > 5 else "MÉDIO" if len(suspicious) > 0 else "BAIXO"
                    st.metric("Risco", risk_level)

                st.markdown("---")

                if not suspicious:
                    st.success("**Excelente!** Nenhuma violação direta encontrada nas transações analisadas.")
                else:
                    st.error(f"**Atenção:** {len(suspicious)} transação(ões) com possível violação de compliance.")

                    # Tabela de transações suspeitas
                    st.markdown('<div class="section-title">Transações com Violações</div>', unsafe_allow_html=True)
                    
                    rows = []
                    for r in suspicious:
                        row = r["row"].copy()
                        row["motivo"] = r.get("reason", "")
                        rows.append(row)
                    sus_df = pd.DataFrame(rows)
                    
                    st.dataframe(
                        sus_df,
                        use_container_width=True,
                        height=400,
                        column_config={
                            "valor": st.column_config.NumberColumn("Valor", format="R$ %.2f"),
                            "motivo": st.column_config.TextColumn("Motivo da Violação", width="large"),
                        }
                    )
                    
                    # Opção para exportar resultados
                    with st.expander("Exportar Resultados"):
                        csv = sus_df.to_csv(index=False)
                        st.download_button(
                            "Baixar Violações (CSV)",
                            csv,
                            file_name=f"violacoes_simples_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )

                # Debug: mostra JSON completo dos resultados
                with st.expander("JSON Completo (Debug)"):
                    st.json(results)
            
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"Erro durante a análise: {str(e)}")
                with st.expander("Detalhes do erro"):
                    st.exception(e)


# Tab 4: Detecção de fraudes contextuais (usando e-mails)
with tabs[3]:
    st.markdown('<h2 class="section-title">Detecção de Fraudes Contextuais</h2>', unsafe_allow_html=True)

    st.info("""
    **Método Avançado:** Cruza dados de transações bancárias com e-mails internos para 
    identificar fraudes que só são detectáveis com **contexto de comunicação** (combinações 
    de desvio de verba, esquemas como WUPHF, Operação Fênix, etc.).
    """)

    st.markdown("---")
    
    # Controles de configuração
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### Configuração da Análise")
        df_ctx = load_transactions()
        max_rows_ctx = st.slider(
            "Número de transações a analisar (com contexto)",
            min_value=5,
            max_value=min(200, len(df_ctx)),
            value=20,
            step=5,
            help="Análise contextual: apenas transações com e-mails relacionados são processadas",
        )
    
    with col2:
        st.markdown("### Escopo")
        st.metric("Transações selecionadas", max_rows_ctx)
        percentage = (max_rows_ctx / len(df_ctx)) * 100
        st.progress(percentage / 100)
        st.caption(f"{percentage:.1f}% do total")

    # Executa a análise contextual
    if st.button("Iniciar Análise Contextual", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("Carregando e-mails internos...")
        progress_bar.progress(10)
        
        status_text.text(f"Cruzando {max_rows_ctx} transações com e-mails...")
        progress_bar.progress(30)
        
        with st.spinner("Analisando contexto e identificando fraudes..."):
            try:
                # Executa análise contextual usando função cacheada
                contextual_results = run_contextual_fraud_cached(max_rows=max_rows_ctx)
                progress_bar.progress(100)
                status_text.empty()

                # Filtra apenas fraudes detectadas
                frauds = [r for r in contextual_results if r.get("fraud_suspected")]

                # Resumo visual dos resultados
                st.markdown("---")
                st.markdown('<div class="section-title">Resultado da Análise Contextual</div>', unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Analisadas", len(contextual_results))
                with col2:
                    st.metric("Fraudes Detectadas", len(frauds), delta=f"-{len(frauds)}" if len(frauds) > 0 else "0")
                with col3:
                    fraud_rate = (len(frauds) / len(contextual_results) * 100) if contextual_results else 0
                    st.metric("Taxa de Fraude", f"{fraud_rate:.1f}%")
                with col4:
                    risk = "CRÍTICO" if len(frauds) > 5 else "MODERADO" if len(frauds) > 0 else "SEGURO"
                    st.metric("Nível de Risco", risk)

                st.markdown("---")

                if not frauds:
                    st.success("**Excelente!** Nenhuma fraude contextual detectada nas transações analisadas.")
                else:
                    st.error(f"**ALERTA:** {len(frauds)} transação(ões) potencialmente fraudulenta(s) detectada(s)!")

                    # Tabela resumida das fraudes
                    st.markdown('<div class="section-title">Transações Fraudulentas (Com Evidências)</div>', unsafe_allow_html=True)
                    
                    rows = []
                    for r in frauds:
                        row = r["row"].copy()
                        row["justificativa"] = r.get("justification", "")[:100] + "..."
                        rows.append(row)
                    fraud_df = pd.DataFrame(rows)
                    
                    st.dataframe(
                        fraud_df,
                        use_container_width=True,
                        height=350,
                        column_config={
                            "valor": st.column_config.NumberColumn("Valor", format="R$ %.2f"),
                            "justificativa": st.column_config.TextColumn("Justificativa", width="large"),
                        }
                    )

                    # Detalhamento individual de cada fraude
                    st.markdown('<div class="section-title">Análise Detalhada por Transação</div>', unsafe_allow_html=True)
                    
                    for idx, r in enumerate(frauds, 1):
                        row = r["row"]
                        with st.expander(f"Transação #{row.get('id_transacao')} - {row.get('descricao')} (R$ {row.get('valor')})"):
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Funcionário", row.get('funcionario', 'N/A'))
                            with col2:
                                st.metric("Categoria", row.get('categoria', 'N/A'))
                            with col3:
                                st.metric("Valor", f"R$ {row.get('valor', 0)}")
                            
                            st.markdown("**Justificativa da Fraude:**")
                            st.markdown(f"""
                            <div class="evidence-box">
                                {r.get('justification', 'Sem justificativa')}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            email_evd = r.get("email_evidence") or []
                            policy_evd = r.get("policy_evidence") or []
                            
                            # Exibe evidências de e-mails
                            if email_evd:
                                st.markdown("**Evidências de E-mails:**")
                                for i, e in enumerate(email_evd, 1):
                                    st.markdown(f"""
                                    <div style="background-color: #fff3cd; padding: 0.75rem; margin: 0.5rem 0; border-radius: 0.25rem; border-left: 4px solid #ff9800;">
                                        <strong>Evidência #{i}:</strong><br>
                                        <em>{e}</em>
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            # Exibe regras de compliance violadas
                            if policy_evd:
                                st.markdown("**Regras de Compliance Violadas:**")
                                for i, p in enumerate(policy_evd, 1):
                                    st.markdown(f"- {p}")
                    
                    # Opção para exportar relatório completo
                    st.markdown("---")
                    with st.expander("Exportar Relatório Completo"):
                        # CSV simples
                        csv = fraud_df.to_csv(index=False)
                        st.download_button(
                            "Baixar Fraudes (CSV)",
                            csv,
                            file_name=f"fraudes_contextuais_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                        
                        # Relatório detalhado em texto
                        report_lines = [f"RELATÓRIO DE FRAUDES CONTEXTUAIS"]
                        report_lines.append(f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}")
                        report_lines.append(f"\nTotal de transações analisadas: {len(contextual_results)}")
                        report_lines.append(f"Fraudes detectadas: {len(frauds)}\n")
                        report_lines.append("="*80)
                        
                        for idx, r in enumerate(frauds, 1):
                            row = r["row"]
                            report_lines.append(f"\n\nFRAUDE #{idx}")
                            report_lines.append(f"ID Transação: {row.get('id_transacao')}")
                            report_lines.append(f"Funcionário: {row.get('funcionario')}")
                            report_lines.append(f"Valor: R$ {row.get('valor')}")
                            report_lines.append(f"Descrição: {row.get('descricao')}")
                            report_lines.append(f"\nJustificativa: {r.get('justification')}")
                            
                            if r.get("email_evidence"):
                                report_lines.append("\nEvidências de E-mails:")
                                for e in r["email_evidence"]:
                                    report_lines.append(f"  - {e}")
                            
                            if r.get("policy_evidence"):
                                report_lines.append("\nRegras Violadas:")
                                for p in r["policy_evidence"]:
                                    report_lines.append(f"  - {p}")
                            
                            report_lines.append("-"*80)
                        report_text = "\n".join(report_lines)
                        st.download_button(
                            "Baixar Relatório Detalhado (TXT)",
                            report_text,
                            file_name=f"relatorio_fraudes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )

                # Debug: mostra JSON completo
                with st.expander("JSON Completo (Debug)"):
                    st.json(contextual_results)
            
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"Erro durante a análise contextual: {str(e)}")
                with st.expander("Detalhes do erro"):
                    st.exception(e)