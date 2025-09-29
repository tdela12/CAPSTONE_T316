from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Routers
from routes import prediction, historical, registration, docs, prefiltered
from routes.errors import register_exception_handlers
from routes.docs import custom_openapi

# Model loader
from models.loader import load_all_models, load_historical_sets, load_rego_data

from config import CORS_ORIGINS, ALLOW_ALL_CORS_DEV
from fastapi.middleware.cors import CORSMiddleware


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
