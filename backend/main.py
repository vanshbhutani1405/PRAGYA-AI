from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import benchmarks, conflicts, documents, expert, graph, query
from services import neo4j_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    neo4j_service.close()


app = FastAPI(title="PRAGYA AI Industrial Knowledge Reasoning Engine", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(query.router)
app.include_router(conflicts.router)
app.include_router(expert.router)
app.include_router(graph.router)
app.include_router(benchmarks.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
