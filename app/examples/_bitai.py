import openai

from app.settings import settings

client = openai.OpenAI(
    api_key=settings.BITAI_TOKEN, base_url="https://litellm.1bitai.ru"
)

response = client.chat.completions.create(
    model="ollama/qwen3.5:35b",  # model to send to the proxy
    messages=[
        {"role": "user", "content": "this is a test request, write a short poem"}
    ],
)

print(response)
print(response.choices[0].message.content)
