from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette_exporter import PrometheusMiddleware
from starlette_exporter.optional_metrics import response_body_size, request_body_size

from app.dependencies import search_service
from app.routers import search, utility
from core.settings import project_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await search_service.create_indices()
    search_service.mystem.start()
    search_service.init_classifiers()
    search_service.load_models()
    yield
    search_service.mystem.close()


app = FastAPI(lifespan=lifespan)
"""
app.add_middleware(
    PrometheusMiddleware,
    app_name=project_settings.app_name,
    skip_paths=["/_/status", "/_/metrics", "/docs", "/redoc"],
    optional_metrics=[response_body_size, request_body_size],
)"""

app.include_router(search.router, prefix="/api")
app.include_router(utility.router, prefix="/_")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=project_settings.host, port=project_settings.port)
