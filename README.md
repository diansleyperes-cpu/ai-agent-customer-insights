# Customer Insights Pipeline

Este projeto implementa uma esteira automatizada de processamento de feedbacks de clientes utilizando multi-agentes (CrewAI) e modelos de linguagem Google Gemini. O objetivo é transformar dados não estruturados de arquivos CSV em relatórios executivos e bases de dados técnicas de forma automatizada.

## Arquitetura do Sistema

O sistema opera com dois agentes especializados que trabalham de forma sequencial:

1. Analista de CX: Extrai o sentimento, categoria e pontos-chave do texto original, validando os dados via Pydantic.
2. Gerente de Sucesso: Recebe a análise técnica e gera uma resposta empática personalizada, além de sugerir ações corretivas para processos internos.

O fluxo garante que apenas dados que respeitem o schema definido em schema.py sejam processados, evitando inconsistências no dashboard final.

## Stack Técnica

- Orquestração: CrewAI
- LLM: Google Gemini (gemini-flash-latest)
- Validação: Pydantic (Strong Typing)
- Configuração: Python 3.10+ e python-dotenv

## Como Executar
1. Preparação do Ambiente:
Crie e ative o ambiente virtual, em seguida instale as dependências:
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

2. Configuração de Credenciais:
Crie um arquivo .env na raiz do projeto (este arquivo é ignorado pelo Git por segurança):
GEMINI_API_KEY=seu_token_aqui

3. Execução:
O script processa o arquivo feedbacks.csv e gera os relatórios em tempo real:
python main.py

## Soluções de Resiliência Implementadas

- Exponential Backoff: Lógica de retry para contornar limites de cota (Erro 429) da API.
- Data Validation: Uso de model_validate_json do Pydantic para garantir integridade entre o output da IA e o relatório final.
- Rate Limiting: Delay programado de 60 segundos entre itens para operação em camadas gratuitas de API.

## Entregáveis

- relatorio_final.md: Dashboard executivo com métricas de sentimento e detalhamento por cliente.
- base_conhecimento.json: Histórico técnico para integração com ferramentas de BI.

---
Nota: Este projeto utiliza .gitignore para proteger credenciais e evitar o versionamento de binários do ambiente virtual.