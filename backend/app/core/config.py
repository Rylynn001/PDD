from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "PDD Trade API"
    API_V1_PREFIX: str = "/api/v1"
    # 允许跨域的前端地址
    CORS_ORIGINS: list[str] = [
        "http://localhost:5500", "http://127.0.0.1:5500",
        "http://localhost:5173", "http://127.0.0.1:5173",
        "null",
    ]


settings = Settings()
