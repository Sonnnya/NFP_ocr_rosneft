from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from app.settings import settings

llm = ChatOpenAI(
    api_key=settings.BITAI_TOKEN,
    base_url="https://litellm.1bitai.ru",
    model="ollama/qwen3.5:35b",
    temperature=0.7,
)

print(llm)


def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


agent = create_agent(
    model=llm,
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
)

print(agent)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "What's the weather in San Francisco?"}]}
)

print(result)

print(result["messages"][-1].content)
