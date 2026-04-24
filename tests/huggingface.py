"""
python -m tests.huggingface
"""

import openai

from app.settings import settings


def ask_model(
    api_key: str = settings.HUGGINGFACEHUB_API_TOKEN,
    content: str = "Столица России?",
    base_url: str = "https://router.huggingface.co/v1",
) -> str:
    client = openai.OpenAI(base_url=base_url, api_key=api_key)

    response = client.chat.completions.create(
        model="Qwen/Qwen3-8B", messages=[{"role": "user", "content": content}]
    )
    return response.choices[0].message.content


def hf_ask_model():
    from huggingface_hub import InferenceClient

    client = InferenceClient(api_key=settings.HUGGINGFACEHUB_API_TOKEN)

    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": "How many 'G's in 'huggingface'?"}],
    )

    return completion.choices[0].message


if __name__ == "__main__":
    answer = ask_model()
    print(answer)

    answer = hf_ask_model()
    print(answer)
