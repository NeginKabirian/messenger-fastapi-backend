from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    LOG_LEVEL: str = "DEBUG"
    ENABLE_CONSOLE_LOG: bool = True
    LOG_FILE_PATH: str = "app.log"
    DATABASE_URL: str
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
