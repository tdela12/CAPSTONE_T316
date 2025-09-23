from fastapi import APIRouter
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.responses import JSONResponse

router = APIRouter(tags=["Docs"])


@router.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Serve a customized Swagger UI"""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="AutoGuru API Docs",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui-bundle.js",
        swagger_css_url="/static/custom-swagger.css",
        swagger_favicon_url="/static/logo.png",
    )


@router.get("/redoc", include_in_schema=False)
async def redoc_html():
    """Serve ReDoc UI"""
    return get_redoc_html(
        openapi_url="/openapi.json",
        title="AutoGuru API (ReDoc)",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
    )


@router.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint(app=None):
    """Expose OpenAPI schema as JSON"""
    from server import app  # avoid circular imports
    return JSONResponse(app.openapi())


def custom_openapi(app):
    """Custom OpenAPI generator (overrides FastAPI’s default)"""
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="AutoGuru — Service Price Prediction API",
        version="1.0.0",
        description="Predict prices for capped, logbook, prescribed and repair services.",
        routes=app.routes,
    )
    openapi_schema["openapi"] = "3.0.3"
    app.openapi_schema = openapi_schema
    return app.openapi_schema
