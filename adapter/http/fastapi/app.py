from adapter.config.loader import load_config
from adapter.config.model import AppConfig
from adapter.http.fastapi.dependencies import APP_CONFIG_STATE
from adapter.http.fastapi.lifespan import app_lifespan
from adapter.http.fastapi.middleware import register_middleware
from adapter.http.fastapi.routers.v1.router import router as v1_router
from fastapi import FastAPI

API_V1_PREFIX = '/api/v1'


def create_app(config: AppConfig | None = None) -> FastAPI:
    app_config = load_config() if config is None else config
    app = FastAPI(title=app_config.app.name, lifespan=app_lifespan)
    setattr(app.state, APP_CONFIG_STATE, app_config)
    register_middleware(app)
    app.include_router(v1_router, prefix=API_V1_PREFIX)
    return app
