import litellm
from litellm import completion

from app.settings import settings

## [OPTIONAL] REGISTER MODEL - not all ollama models support function calling, litellm defaults to json mode tool calls if native tool calling not supported.

litellm.register_model({"ollama_chat/qwen3.5:35b": {"supports_function_calling": True}})
litellm.set_verbose = True

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        },
    }
]

messages = [
    {"role": "system", "content": "/no_think"},
    {"role": "user", "content": "What's the weather like in Boston today?"},
]


response = completion(
    model="openai/ollama/qwen3.5:35b",
    messages=messages,
    tools=tools,
    api_key=settings.BITAI_TOKEN,
    api_base="https://litellm.1bitai.ru",
)


print(response)
