from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from app.api.routes.files import router as files_router
from app.core.config import get_settings

_settings = get_settings()

app = FastAPI()

CORS_ORIGINS = [o.strip() for o in _settings.CORS_ORIGINS.split(",")]


app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
# app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY", "secret-key"))

app.include_router(files_router, prefix="/files")

APP_ROOT = Path(__file__).resolve().parent
uploads_dir = APP_ROOT / "../data/uploads"

app.mount("/data/uploads", StaticFiles(directory=uploads_dir), name="uploads")



def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="File Management API",
        version="1.0.0",
        description="File management API",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi