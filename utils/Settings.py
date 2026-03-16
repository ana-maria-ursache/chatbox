from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int = 30
    pg_database_url: str
    model_config = SettingsConfigDict(env_file=".env")


# Instantiate once to be imported elsewhere
settings = Settings()
