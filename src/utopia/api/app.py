"""Utopia FastAPI application.

Minimal bootstrap — routes added per bounded context as they are built.
"""

from fastapi import FastAPI

app = FastAPI(
    title="Utopia",
    description="Private cognitive operating system and judgment refinery",
    version="0.1.0",
)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
