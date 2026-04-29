import uvicorn
from fastapi import FastAPI

from app.api import packages_router
from app.settings import settings, setup_logging

setup_logging()

app = FastAPI()

app.include_router(packages_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        log_level=settings.LOG_LEVEL,
        reload=settings.RELOAD,
    )
