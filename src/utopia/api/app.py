"""Utopia FastAPI application.

Minimal bootstrap — routes added per bounded context as they are built.
"""

from fastapi import FastAPI

from utopia.api.routes.aether import router as aether_router
from utopia.api.routes.evidence import router as evidence_router
from utopia.api.routes.execution import router as execution_router
from utopia.api.routes.physiology import router as physiology_router
from utopia.api.routes.reasoning import router as reasoning_router
from utopia.api.routes.review import router as review_router
from utopia.api.routes.vector import router as vector_router

app = FastAPI(
    title="Utopia",
    description="Private cognitive operating system and judgment refinery",
    version="0.1.0",
)

app.include_router(vector_router)
app.include_router(evidence_router)
app.include_router(execution_router)
app.include_router(physiology_router)
app.include_router(aether_router)
app.include_router(reasoning_router)
app.include_router(review_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
