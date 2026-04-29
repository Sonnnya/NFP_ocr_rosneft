import logging
import os
import sys

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    HUGGINGFACEHUB_API_TOKEN: str
    HF_INFERENCE_ENDPOINT: str
    MODEL: str = "microsoft/Phi-3-mini-4k-instruct"
    PORT: int = 8000
    LOG_LEVEL: str = "debug"
    RELOAD: bool = True
    BITAI_TOKEN: str = "sk-ключ"

    class Config:
        env_file = ".env"
        extra = "ignore"


def setup_env(settings: Settings):
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = settings.HUGGINGFACEHUB_API_TOKEN
    os.environ["HF_INFERENCE_ENDPOINT"] = settings.HF_INFERENCE_ENDPOINT


_SEPARATOR = "─" * 72


def setup_logging() -> None:
    level = logging.getLevelName(settings.LOG_LEVEL.upper())

    fmt = "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s"
    datefmt = "%H:%M:%S"

    logging.basicConfig(
        level=level,
        format=fmt,
        datefmt=datefmt,
        stream=sys.stdout,
        force=True,  # override any handlers uvicorn already set up
    )

    # Keep uvicorn and httpx quieter unless we're at DEBUG ourselves
    if level > logging.DEBUG:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)


def log_blob(logger: logging.Logger, label: str, text: str) -> None:
    """
    Log a large text blob (OCR output, LLM response) at DEBUG level
    with a visible header and footer so it's easy to spot in the console.

        ─── OCR result: АО форма 2.jpg ────────────────────────────────
        ООО «Ромашка»
        Авансовый отчет № 47
        ...
        ───────────────────────────────────────────────────────────────
    """
    if not logger.isEnabledFor(logging.DEBUG):
        return

    header = f"─── {label} " + "─" * max(0, len(_SEPARATOR) - len(label) - 5)
    logger.debug("\n%s\n%s\n%s", header, text.strip(), _SEPARATOR)


settings = Settings()
