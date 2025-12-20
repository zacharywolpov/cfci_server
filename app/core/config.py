import os
import dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

dotenv.load_dotenv(".env.development.local")

class Settings(BaseSettings):
    app_name: str = "cfci_server"
    environment: str = "development"
    debug: bool = True

    # Keys and auth
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY")

    # Client origins
    CORS_ORIGINS: str = ""

    # API settings and keys
    openai_key: str
    airtable_api_key: str
    postgres_url: str

    model_config: SettingsConfigDict = {
        "env_file": (
            ".env.development",
            ".env.development.local"
        ),
        "env_file_encoding": "utf-8",
    }

    # Cors origin list
    @property
    def cors_origin_list(self):
        if not self.CORS_ORIGINS:
            return []
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()