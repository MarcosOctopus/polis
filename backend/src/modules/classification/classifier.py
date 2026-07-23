"""IA classifier for Polis messages.

Uses OpenAI (or fallback) to classify citizen messages into types,
sentiment, urgency, risk, categories, and extract location data.
"""

import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Default classification returned when the LLM call fails
_FALLBACK = {
    "classification_type": "general",
    "category": None,
    "subcategory": None,
    "sentiment": "neutro",
    "sentiment_score": 0.5,
    "urgency": "baixa",
    "risk": "baixo",
    "extracted_address": None,
    "extracted_neighborhood": None,
    "extracted_city": None,
    "extracted_state": None,
    "reference_point": None,
    "latitude": None,
    "longitude": None,
    "geocode_source": None,
    "suggested_department": None,
    "summary": None,
    "keywords": [],
    "confidence": 0.1,
}

_SYSTEM_PROMPT = """Você é um assistente especializado em classificar mensagens de cidadãos para a Prefeitura de São Paulo.

Analise a mensagem e retorne UM OBJETO JSON válido com os seguintes campos:

1. `classification_type` (string, obrigatório): Classifique a mensagem em UM dos tipos:
   - "complaint" (reclamação)
   - "praise" (elogio)
   - "suggestion" (sugestão)
   - "question" (dúvida/pergunta)
   - "denunciation" (denúncia)
   - "support" (pedido de suporte/ajuda)
   - "criticism" (crítica)
   - "emergency" (emergência — risco iminente à vida ou patrimônio)
   - "general" (geral — não se encaixa em nenhum acima)

2. `category` (string opcional): Categoria temática. Exemplos:
   "infraestrutura", "saude", "educacao", "seguranca", "transporte", "meio_ambiente",
   "habitacao", "assistencia_social", "cultura", "esporte_lazer", "limpeza_urbana",
   "iluminacao_publica", "saneamento_basico", "mobilidade_urbana", "obras",
   "servicos_publicos", "orcamento", "zoneamento"

3. `subcategory` (string opcional): Subcategoria mais específica, ex: "buraco_rua", "coleta_lixo"

4. `sentiment` (string opcional): "positivo", "negativo", ou "neutro"

5. `sentiment_score` (float opcional, 0.0 a 1.0): 0=muito negativo, 0.5=neutro, 1.0=muito positivo

6. `urgency` (string opcional): "baixa", "media", "alta", ou "emergencia"

7. `risk` (string opcional): "baixo", "medio", ou "alto"

8. `extracted_address` (string opcional): Endereço mencionado na mensagem

9. `extracted_neighborhood` (string opcional): Bairro mencionado

10. `extracted_city` (string opcional): Cidade mencionada

11. `extracted_state` (string opcional): Estado mencionado (sigla)

12. `reference_point` (string opcional): Ponto de referência mencionado

13. `latitude` (float opcional): Latitude se coordenada for mencionada

14. `longitude` (float opcional): Longitude se coordenada for mencionada

15. `suggested_department` (string opcional): Secretaria ou departamento responsável sugerido

16. `summary` (string opcional, máximo 300 caracteres): Resumo da mensagem

17. `keywords` (array de strings opcional): Palavras-chave relevantes (máximo 8)

IMPORTANTE: Responda APENAS com o JSON. Sem texto adicional, sem explicações, sem markdown.
"""


class MessageClassifier:
    """Classifies messages using OpenAI or a fallback strategy."""

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self._client = None
        logger.info("MessageClassifier initialized with API key length=%d", len(api_key) if api_key else 0)

    # ------------------------------------------------------------------
    # Lazy-loaded OpenAI client
    # ------------------------------------------------------------------
    @property
    def client(self):
        if self._client is None:
            try:
                from openai import AsyncOpenAI

                self._client = AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                logger.warning("openai package not installed; classifier will use fallback")
                self._client = None
        return self._client

    # ------------------------------------------------------------------
    # Public classify method
    # ------------------------------------------------------------------
    async def classify(
        self,
        text: str,
        message_id: str,
        contact_info: dict | None = None,
    ) -> dict:
        """Classify a message text.

        Args:
            text: The message text to classify.
            message_id: Unique identifier of the message (for logging).
            contact_info: Optional dict with contact metadata (e.g. city, neighborhood).

        Returns:
            A dict with all classification fields. On error, returns a
            low-confidence fallback with classification_type="general".
        """
        if not text or not text.strip():
            logger.warning("classify called with empty text (msg=%s)", message_id)
            return dict(_FALLBACK)

        # Build user prompt with optional contact context
        prompt = self._build_prompt(text, contact_info)

        try:
            if self.client:
                result = await self._call_openai(prompt)
            else:
                result = dict(_FALLBACK)
                logger.info("No OpenAI client available; using fallback for msg=%s", message_id)
        except Exception:
            logger.exception("LLM call failed for msg=%s; using fallback", message_id)
            result = dict(_FALLBACK)

        # Ensure all expected keys exist
        result = {**_FALLBACK, **result}
        # Stamp processed_at
        result["processed_at"] = datetime.now(timezone.utc).isoformat()
        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _build_prompt(self, text: str, contact_info: dict | None = None) -> str:
        """Build the user prompt."""
        parts = [f"Classifique a seguinte mensagem de cidadão:\n\n{text}"]
        if contact_info:
            ctx = []
            if contact_info.get("city"):
                ctx.append(f"Cidade do contato: {contact_info['city']}")
            if contact_info.get("neighborhood"):
                ctx.append(f"Bairro do contato: {contact_info['neighborhood']}")
            if contact_info.get("state"):
                ctx.append(f"Estado do contato: {contact_info['state']}")
            if ctx:
                parts.append("\n\nContexto do contato:\n" + "\n".join(ctx))
        return "\n".join(parts)

    async def _call_openai(self, prompt: str) -> dict:
        """Call OpenAI chat completion and parse JSON response."""
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=1024,
            response_format={"type": "json_object"},
        )

        choice = response.choices[0]
        message = choice.message
        if not message or not message.content:
            logger.warning("OpenAI returned empty response; using fallback")
            return dict(_FALLBACK)

        content = message.content.strip()
        return json.loads(content)
