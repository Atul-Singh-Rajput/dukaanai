from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "DukaanAI API"
    environment: str = "development"
    database_url: str = "sqlite:///./dukaanai.db"
    frontend_origin: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
