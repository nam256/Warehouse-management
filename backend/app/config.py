from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    app_name: str = "Oxeyns Warehouse & Production API"
    database_url: str = "sqlite:///./oxeyns.db"
    secret_key: str = "dev-secret-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174"
    ai_assistant_enabled: bool = False
    ai_provider: str = "none"
    ai_api_key: str | None = None
    ai_model: str = "gpt-4o-mini"
    ai_base_url: str | None = None

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

settings = Settings()
