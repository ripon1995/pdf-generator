from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gemini_api_key: str
    gemini_model: str = "gemini-2.5-flash"
    google_drive_folder_id: str
    google_oauth_client_secret_file: str = "client_secret.json"
    google_oauth_token_file: str = "token.json"

    model_config = {"env_file": ".env"}


settings = Settings()
