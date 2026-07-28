from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    LOG_LEVEL: str = "INFO"
    ENABLE_CONSOLE_LOG: bool = True
    LOG_FILE_PATH: str = "app.log"

    class Config:
        env_file = ".env"


# model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
