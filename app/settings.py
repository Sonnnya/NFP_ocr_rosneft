import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    HUGGINGFACEHUB_API_TOKEN: str
    HF_INFERENCE_ENDPOINT: str
    MODEL: str = "microsoft/Phi-3-mini-4k-instruct"
    PORT: int = 8000
    LOG_LEVEL: str = "debug"

    class Config:
        env_file = ".env"


def setup_env(settings: Settings):
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = settings.HUGGINGFACEHUB_API_TOKEN
    os.environ["HF_INFERENCE_ENDPOINT"] = settings.HF_INFERENCE_ENDPOINT


settings = Settings()
