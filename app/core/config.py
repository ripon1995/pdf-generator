from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    grok_api_key: str
    grok_model: str = "grok-2-vision-1212"

    model_config = {"env_file": ".env"}


settings = Settings()
