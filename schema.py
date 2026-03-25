from pydantic import BaseModel, Field
from typing import List, Literal

class AnaliseSentimento(BaseModel):
    """Esquema para a análise técnica do feedback"""
    # Usando Literal, a IA é obrigada a escolher exatamente uma dessas strings
    sentimento: Literal["MUITO POSITIVO", "POSITIVO", "NEUTRO", "NEGATIVO", "CRÍTICO"] = Field(
        description="Classificação categórica do sentimento do cliente"
    )
    score_confianca: float = Field(description="Confiança da análise de 0 a 1", ge=0, le=1)
    assunto_principal: str = Field(description="O tópico principal (ex: Entrega, Qualidade do Produto, Preço, Atendimento)")
    pontos_chave: List[str] = Field(description="Lista de 2 ou 3 pontos específicos mencionados pelo cliente")
    urgencia_resolucao: bool = Field(description="Verdadeiro se houver xingamentos ou ameaça de processo")

class SugestaoResposta(BaseModel):
    """Esquema para a resposta estratégica ao cliente"""
    tom_de_voz: str = Field(description="O tom usado na resposta (ex: Empático, Formal, Pragmático)")
    texto_resposta: str = Field(description="A resposta completa sugerida para enviar ao cliente")
    acao_interna: str = Field(description="O que a empresa deve fazer internamente para resolver o problema permanentemente")