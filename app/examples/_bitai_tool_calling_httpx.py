import json

import httpx

from app.settings import settings

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        },
    }
]

payload = {
    "model": "ollama/qwen3.5:35b",
    "messages": [
        {"role": "user", "content": "What's the weather like in Boston today?"}
    ],
    "tools": tools,
}

response = httpx.post(
    "https://litellm.1bitai.ru/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {settings.BITAI_TOKEN}",
        "Content-Type": "application/json",
    },
    json=payload,
    timeout=500,
)

raw = response.json()
print(json.dumps(raw, indent=2))  # ← see exactly what the proxy returns
