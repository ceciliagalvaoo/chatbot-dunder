# Toby Auditor — Sistema de Auditoria Inteligente da Dunder Mifflin


## Introdução

Este projeto foi desenvolvido com o objetivo de aplicar técnicas modernas de Inteligência Artificial ao contexto de auditoria corporativa. Inspirado no universo fictício de *The Office*, o sistema foi criado para auxiliar Toby Flenderson na identificação de violações de compliance, possíveis fraudes financeiras e comportamentos suspeitos revelados em e-mails corporativos.

Utilizando modelos de linguagem executados na Groq API, juntamente com Recuperação Aumentada por Geração (RAG) e análise de contexto multiagente, o sistema apresenta respostas fundamentadas, explicáveis e auditáveis. Sua interface Streamlit possibilita demonstração intuitiva do fluxo de auditoria, enquanto a arquitetura modular permite fácil expansão e manutenção.

Este documento descreve a estrutura do projeto, sua lógica interna, arquitetura multiagente, fluxo operacional e diretrizes para execução.

## Vídeo de Demonstração

(Insira o link aqui)

## Integrantes

* Cecília Beatriz Melo Galvão
* Mariella Sayumi Mercado Kamezawa
* Pablo de Azevedo


## Estrutura do Projeto

```
dunder-auditor/
├── data/
│   ├── politica_compliance.txt
│   ├── emails_internos.txt
│   ├── transacoes_bancarias.csv
│
├── src/
│   ├── llm_client.py
│   ├── retriever_compliance.py
│   ├── chatbot_compliance.py
│   ├── conspiracy_detector.py
│   ├── fraud_detector_simple.py
│   ├── fraud_detector_contextual.py
│   ├── orchestrator_demo.py
│
├── streamlit_app.py
├── requirements.txt
├── .env.example
└── README.md
```


## Arquitetura da Solução

O sistema é composto por múltiplos agentes especializados, todos apoiados por um núcleo comum de comunicação com a Groq API. Cada agente executa uma tarefa específica do processo de auditoria, colaborando dentro de uma arquitetura modular e transparente.

### 1. Núcleo de LLM (`llm_client.py`)

Camada responsável por:

* chamada unificada aos modelos Groq,
* respostas em texto e JSON,
* embeddings locais via hashing (para RAG),
* mecanismo de throttling para evitar limites de tokens por minuto,
* sanitização e robustez de parsing.

### 2. Recuperação de Contexto (RAG) (`retriever_compliance.py`)

* Indexa a política de compliance em pequenos trechos,
* gera embeddings locais,
* localiza trechos mais relevantes para cada pergunta ou transação,
* mitiga alucinações, pois o modelo responde com base em evidências textuais.

### 3. Chatbot de Compliance (`chatbot_compliance.py`)

* Usa RAG para responder a perguntas com fundamentação normativa,
* devolve evidências textuais usadas,
* estrutura ideal para consultas internas de políticas corporativas.

### 4. Detector de Conspiração (`conspiracy_detector.py`)

* Fragmenta o arquivo de e-mails em blocos,
* avalia cada bloco separadamente,
* identifica hostilidade, sabotagem ou operações clandestinas contra Toby,
* agrega as evidências em um relatório final.

### 5. Fraudes Diretas (`fraud_detector_simple.py`)

* Analisa transações isoladas à luz da política,
* identifica violações explícitas (categoria proibida, valor irregular etc.),
* modo demo limita número de transações para respeitar limites de token.

### 6. Fraudes Contextuais (`fraud_detector_contextual.py`)

* Cruza transações com e-mails relacionados ao funcionário/valor,
* identifica fraude que depende de contexto (conluio, manipulação, Operação Fênix),
* produz justificativa e evidências baseadas tanto em e-mails quanto na política.

### 7. Interface Web (Streamlit)

* Quatro módulos principais:

  1. Chatbot de compliance
  2. Conspiração
  3. Fraudes diretas
  4. Fraudes contextuais
* Modo demo parametrizável,
* exibição de DataFrames e JSON bruto,
* ideal para demonstração prática.


## Fluxo do Agente

A seguir, é apresentado o fluxo geral do agente de auditoria, do momento da requisição até a produção de evidências e respostas.

### 1. Recebimento da Solicitação

O sistema inicia com uma entrada do usuário, que pode ser:

* uma pergunta sobre compliance,
* um pedido de verificação de conspiração,
* uma transação individual ou conjunto de transações,
* ou a análise de fraude contextual com e-mails.

Cada tipo de solicitação direciona o fluxo para um agente específico.

### 2. Pré-Processamento e Recuperação de Contexto

Antes de consultar o LLM:

* o sistema identifica palavras-chave,
* prepara o prompt com informações estruturadas,
* aplica RAG quando necessário (compliance e fraudes),
* recupera trechos relevantes da política ou e-mails relacionados ao funcionário.

Esse passo garante que as respostas sejam sempre baseadas em evidência documental.

### 3. Chamada ao Modelo LLM

O módulo `llm_client`:

* monta a mensagem com instruções claras,
* executa a chamada ao modelo configurado na Groq API,
* aplica controle de taxa (throttling),
* assegura respostas bem estruturadas (JSON quando necessário).

Essa etapa é abstraída, de forma que cada agente apenas “solicita” uma resposta e o cliente LLM cuida do restante.

### 4. Pós-Processamento e Validação

Após a resposta do modelo:

* ocorre validação do JSON com correção robusta,
* extração de campos essenciais,
* identificação de violações,
* consolidação de justificativas e evidências,
* registro de trechos relevantes para auditoria.

Agentes diferentes aplicam validações diferentes:

* Fraudes diretas verificam regras explícitas,
* Fraudes contextuais avaliam coerência entre e-mails e transação,
* Conspiração examina sinais agregados de hostilidade e operações secretas.

### 5. Geração de Saída Interpretável

Por fim, o agente entrega:

* uma resposta estruturada,
* evidências textuais,
* decisão Boolean (fraude, conspiração, violação),
* justificativas detalhadas.

No Streamlit, esses resultados são apresentados em tabelas, métricas e expansores.

### 6. Garantia de Auditabilidade

O sistema permite:

* rastreio do trecho da política utilizado,
* rastreio dos trechos de e-mail citados,
* rastreio da transação original analisada.

Esse fluxo garante transparência, precisão e reprodutibilidade — cruciais para auditoria.


## Como Rodar Localmente

### 1. Configurar `.env`

```
GROQ_API_KEY=SEU_TOKEN_AQUI
GROQ_MODEL=llama-3.1-8b-instant
```

### 2. Instalar dependências

```bash
python -m pip install -r requirements.txt
```

### 3. Rodar Streamlit

```bash
streamlit run streamlit_app.py
```

### 4. Executar CLI

```bash
python -m src.orchestrator_demo
```

## Observações sobre Limites da Groq

Devido aos limites de tokens por minuto e por dia, foram implementadas:

* Execução em modo demo (limite de transações),
* Redução de contexto quando possível,
* mecanismo de pausa (throttling) no cliente LLM.

Esses ajustes não afetam a qualidade do raciocínio do modelo, apenas evitam erros de rate-limit.

## Conclusão

O Toby Auditor demonstra como agentes baseados em LLM podem ser integrados em um fluxo completo de auditoria corporativa, envolvendo compliance, análise contextual, identificação de fraudes e inspeção de comunicações internas. A solução cumpre integralmente os requisitos do desafio, fornecendo evidências conclusivas e interpretações fundamentadas dos documentos analisados.

A arquitetura modular permite evolução futura, como integração com bancos de dados, dashboards históricos ou aumento da granularidade das regras de compliance. O sistema serve como protótipo funcional de como IA generativa pode fortalecer processos de governança, risco e compliance dentro de organizações modernas.

