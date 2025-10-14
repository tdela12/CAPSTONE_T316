from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
import uuid
from datetime import datetime
from fastapi.staticfiles import StaticFiles
import logging

# Routers
from routes import prediction, historical, registration, docs, prefiltered
from routes.errors import register_exception_handlers
from routes.docs import custom_openapi

# Model loader
from models.loader import load_all_models, load_historical_sets, load_rego_data

from config import CORS_ORIGINS, ALLOW_ALL_CORS_DEV
from fastapi.middleware.cors import CORSMiddleware

# Setup Server logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(trace_id)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)

logger = logging.getLogger("server")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.models = load_all_models()
    app.state.historical_sets = load_historical_sets()
    app.state.rego_data = load_rego_data()
    print("Models and datasets loaded successfully!")
    yield  


    print("Shutting down app")

def create_app() -> FastAPI:
    app = FastAPI(
        title="AutoGuru — Service Price Prediction API",
        description="Predict prices for capped, logbook, prescribed, and repair services.",
        version="1.0.0",
        docs_url=None,
        redoc_url=None,
        lifespan=lifespan  # use lifespan instead of deprecated on_event
    )

    # Serve static assets
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # Override OpenAPI schema
    app.openapi = lambda: custom_openapi(app)

    # Register routers
    app.include_router(prediction.router)
    app.include_router(historical.router)
    app.include_router(registration.router)
    app.include_router(docs.router)
    app.include_router(prefiltered.router)

    # Register global exception handlers
    register_exception_handlers(app)

    if ALLOW_ALL_CORS_DEV:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
    )

    return app


# For running via: uvicorn server:app --reload
app = create_app()

@app.middleware("http")
async def add_trace_id(request: Request, call_next):
    trace_id = request.headers.get("X-Trace-ID", f"TR-{uuid.uuid4().hex[:8].upper()}")
    request.state.trace_id = trace_id

    old_factory = logging.getLogRecordFactory()
    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        record.trace_id = trace_id
        return record
    logging.setLogRecordFactory(record_factory)

    response = await call_next(request)
    response.headers["X-Trace-ID"] = trace_id
    return response

logger.info("Server started successfully", extra={"trace_id": "SYSTEM"})
