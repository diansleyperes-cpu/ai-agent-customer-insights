import os
import time
import csv
import json
from dotenv import load_dotenv
from schema import AnaliseSentimento, SugestaoResposta
from langchain_google_genai import ChatGoogleGenerativeAI

# 1. CONFIGURAÇÕES INICIAIS
load_dotenv()
os.environ["google_api_version"] = "v1"

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise RuntimeError("GEMINI_API_KEY não configurada no arquivo .env")

# 2. CONFIGURAÇÃO DO MODELO
gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest", 
    google_api_key=gemini_api_key,
    temperature=0.1
)

# 3. PIPELINES E PROMPTS
analise_chain = gemini_llm.with_structured_output(AnaliseSentimento)
resposta_chain = gemini_llm.with_structured_output(SugestaoResposta)


def build_analysis_prompt(feedback_text):
    return (
        "Você é um analista senior de customer experience. "
        "Analise o feedback do cliente e responda somente com os campos do schema solicitado. "
        "Classifique o sentimento, estime a confiança entre 0 e 1, identifique o assunto principal, "
        "liste de 2 a 3 pontos-chave e marque urgencia_resolucao como true apenas quando houver ofensa grave, "
        "ameaça de processo ou forte risco de churn imediato.\n\n"
        f"Feedback do cliente:\n{feedback_text}"
    )


def build_response_prompt(feedback_text, analise):
    return (
        "Você é um gerente de sucesso do cliente. "
        "Com base no feedback original e na análise técnica estruturada, gere uma resposta empática ao cliente "
        "e uma ação interna objetiva para evitar recorrência. "
        "Responda apenas com os campos do schema solicitado.\n\n"
        f"Feedback do cliente:\n{feedback_text}\n\n"
        "Análise técnica:\n"
        f"{json.dumps(analise.model_dump(), ensure_ascii=False, indent=2)}"
    )


# 4. FUNÇÃO DE APOIO: RETRY PARA COTA DE API
def invoke_with_retry(operation, max_attempts=5, initial_delay=30):
    for attempt in range(1, max_attempts + 1):
        try:
            return operation()
        except Exception as e:
            msg = str(e).lower()
            if '429' in msg or 'quota' in msg or 'limit' in msg:
                if attempt == max_attempts: raise
                delay = initial_delay * attempt
                print(f"⚠️ Cota excedida. Tentativa {attempt}/{max_attempts}. Aguardando {delay}s...")
                time.sleep(delay)
            else:
                raise


def analisar_feedback(feedback_text):
    return invoke_with_retry(
        lambda: analise_chain.invoke(build_analysis_prompt(feedback_text))
    )


def gerar_resposta(feedback_text, analise):
    return invoke_with_retry(
        lambda: resposta_chain.invoke(build_response_prompt(feedback_text, analise))
    )

# 5. EXECUÇÃO EM LOTE (BATCH)
if __name__ == "__main__":
    print("\n🚀 Iniciando Inteligência de Dados em Lote...")
    
    estatisticas = {
        "total": 0,
        "sentimentos": {"MUITO POSITIVO": 0, "POSITIVO": 0, "NEUTRO": 0, "NEGATIVO": 0, "CRÍTICO": 0},
        "categorias": {}
    }
    
    corpo_relatorio = ""
    lista_historico_json = []

    try:
        if not os.path.exists('feedbacks.csv'):
            print("❌ Arquivo 'feedbacks.csv' não encontrado!")
        else:
            with open('feedbacks.csv', mode='r', encoding='utf-8') as file:
                leitor = csv.DictReader(file)
                
                for linha in leitor:
                    id_cliente = linha.get('id', 'N/A')
                    feedback = linha.get('comentario', '')
                    
                    print(f"\n🔎 Processando Item #{id_cliente}...")
                    
                    try:
                        res_analise = analisar_feedback(feedback)

                        if res_analise:
                            res_resposta = gerar_resposta(feedback, res_analise)
                            sentimento_final = res_analise.sentimento.upper()
                            assunto_final = res_analise.assunto_principal
                            
                            estatisticas["total"] += 1
                            estatisticas["sentimentos"][sentimento_final] = estatisticas["sentimentos"].get(sentimento_final, 0) + 1
                            estatisticas["categorias"][assunto_final] = estatisticas["categorias"].get(assunto_final, 0) + 1

                            lista_historico_json.append({
                                "id": id_cliente,
                                "analise": res_analise.model_dump(),
                                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                            })

                            corpo_relatorio += f"### 👤 Feedback #{id_cliente} | {sentimento_final}\n"
                            corpo_relatorio += f"**Assunto:** {assunto_final}\n"
                            corpo_relatorio += f"**Confiança da Análise:** {res_analise.score_confianca:.2f}\n"
                            corpo_relatorio += f"**Urgência de Resolução:** {'Sim' if res_analise.urgencia_resolucao else 'Não'}\n"
                            corpo_relatorio += f"**Pontos Chave:** {', '.join(res_analise.pontos_chave)}\n\n"
                            
                            if res_resposta:
                                corpo_relatorio += f"**Tom de Voz:** {res_resposta.tom_de_voz}\n"
                                corpo_relatorio += f"**Resposta:** {res_resposta.texto_resposta}\n"
                                corpo_relatorio += f"**Ação Interna:** {res_resposta.acao_interna}\n\n"
                            
                            corpo_relatorio += "---\n\n"
                            print(f"✅ Item #{id_cliente} validado com Pydantic!")

                    except Exception as e_item:
                        print(f"⚠️ Falha na validação Pydantic do item {id_cliente}: {e_item}")

                    time.sleep(60)

            # --- FINALIZAÇÃO: Gravação dos Arquivos ---
            print("\n📊 Finalizando Relatórios...")
            dashboard = "# 📊 DASHBOARD DE CUSTOMER INSIGHTS\n\n"
            dashboard += f"**Total processado:** {estatisticas['total']}\n\n"
            dashboard += "### 🎭 Sentimentos\n"
            
            for s, q in estatisticas['sentimentos'].items():
                if estatisticas['total'] > 0:
                    dash_icon = "🟩" if "POSITIVO" in s else "🟥" if s in ["NEGATIVO", "CRÍTICO"] else "🟨"
                    dashboard += f"- {dash_icon} **{s}:** {q} ({(q/estatisticas['total'])*100:.1f}%)\n"
            
            dashboard += "\n### 📂 Categorias\n"
            for c, q in estatisticas['categorias'].items():
                dashboard += f"- **{c}:** {q}\n"
            
            with open("relatorio_final.md", "w", encoding="utf-8") as f:
                f.write(dashboard + "\n## 📝 DETALHAMENTO\n\n" + corpo_relatorio)

            with open("base_conhecimento.json", "w", encoding="utf-8") as f:
                json.dump(lista_historico_json, f, indent=4, ensure_ascii=False)

            print("\n🏆 TUDO PRONTO! Verifique 'relatorio_final.md' e 'base_conhecimento.json'")

    except Exception as e_geral:
        print(f"❌ Erro crítico no sistema: {e_geral}")