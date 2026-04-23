import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    HUGGINGFACEHUB_API_TOKEN: str
    MODEL: str = "microsoft/Phi-3-mini-4k-instruct"

    class Config:
        env_file = ".env"


def setup_env(settings: Settings):
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = settings.HUGGINGFACEHUB_API_TOKEN


settings = Settings()
