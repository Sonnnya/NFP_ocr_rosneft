import openai

from app.settings import settings

client = openai.OpenAI(
    api_key=settings.BITAI_TOKEN, base_url="https://litellm.1bitai.ru"
)


def ask_model(question: str) -> str:
    response = client.chat.completions.create(
        model="ollama/qwen3.5:35b",
        messages=[{"role": "user", "content": question}],
    )
    return response.choices[0].message.content
