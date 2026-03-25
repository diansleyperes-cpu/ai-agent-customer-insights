# Customer Insights Pipeline

Este projeto processa feedbacks de clientes a partir de um arquivo CSV e gera dois artefatos de saída:

- um dashboard em Markdown com métricas agregadas e detalhamento por item
- uma base JSON com o histórico estruturado das análises

O pipeline usa Google Gemini com saídas estruturadas via Pydantic, sem orquestração por CrewAI. O objetivo é transformar comentários livres em análises consistentes e respostas sugeridas para atendimento.

## Arquitetura do Sistema

O fluxo atual executa duas etapas sequenciais para cada feedback:

1. Análise técnica do comentário
	- classifica sentimento
	- estima score de confiança
	- identifica assunto principal
	- extrai pontos-chave
	- marca urgência de resolução

2. Geração de resposta sugerida
	- produz uma resposta empática ao cliente
	- define tom de voz
	- sugere uma ação interna corretiva

As duas etapas usam schemas definidos em [schema.py](schema.py), garantindo estrutura e tipos antes de gravar os resultados finais.

## Stack Técnica

- LLM: Google Gemini `gemini-flash-latest`
- Integração com modelo: `langchain-google-genai`
- Validação estruturada: Pydantic v2
- Configuração de ambiente: `python-dotenv`
- Linguagem: Python

## Estrutura do Projeto

- [main.py](main.py): pipeline principal de processamento em lote
- [schema.py](schema.py): modelos Pydantic para análise e resposta
- [feedbacks.csv](feedbacks.csv): entrada com os comentários dos clientes
- [relatorio_final.md](relatorio_final.md): dashboard consolidado em Markdown
- [base_conhecimento.json](base_conhecimento.json): histórico técnico em JSON

## Como Executar

1. Preparação do ambiente

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

2. Configuração de credenciais

Crie um arquivo `.env` na raiz do projeto:

```env
GEMINI_API_KEY=seu_token_aqui
```

3. Execução do lote

```powershell
.\.venv\Scripts\python.exe .\main.py
```

O script lê [feedbacks.csv](feedbacks.csv), processa cada linha e atualiza os arquivos finais ao término do lote.

## Resiliência Implementada

- Retry com backoff progressivo para erros de cota, limite ou resposta `429`
- Validação estruturada com Pydantic para análise e resposta
- Delay de 60 segundos entre itens para reduzir risco de estouro de cota em camadas gratuitas
- Tratamento isolado por item para evitar que uma falha interrompa todo o lote

## Formato de Entrada

O arquivo [feedbacks.csv](feedbacks.csv) deve conter pelo menos estas colunas:

- `id`
- `comentario`

## Entregáveis

- [relatorio_final.md](relatorio_final.md): resumo executivo com total processado, distribuição de sentimentos, categorias e detalhamento por feedback
- [base_conhecimento.json](base_conhecimento.json): lista estruturada com `id`, `analise` e `timestamp`

## Observações

- O pipeline depende da variável `GEMINI_API_KEY`; sem ela, a execução falha imediatamente.
- O arquivo `.env` não deve ser versionado.
- O arquivo `requirements.txt` contém dependências adicionais do ambiente, mas a execução principal depende diretamente de `python-dotenv`, `pydantic` e `langchain-google-genai`.