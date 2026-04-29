import logging

import openai

from app.settings import log_blob, settings

client = openai.OpenAI(
    api_key=settings.BITAI_TOKEN, base_url="https://litellm.1bitai.ru"
)

logger = logging.getLogger(__name__)


def ask_model(question: str) -> str:
    logger.debug("Asking model...")
    response = client.chat.completions.create(
        model="ollama/qwen3.5:35b",
        messages=[{"role": "user", "content": question}],
    )
    log_blob(logger, "LLM response", response.choices[0].message.content)
    return response.choices[0].message.content
