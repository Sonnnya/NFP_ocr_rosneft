from langchain.agents import create_agent
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

from .settings import settings, setup_env

setup_env(settings)

llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen3-8B",
    provider="auto",
    huggingfacehub_api_token=settings.HUGGINGFACEHUB_API_TOKEN,
)
model = ChatHuggingFace(llm=llm)

print(model.invoke("What is Deep Learning?"))


def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


agent = create_agent(
    model=model,
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "What's the weather in San Francisco?"}]}
)
print(result["messages"][-1].content_blocks)
