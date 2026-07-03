from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    huggingface_api_key: str = ""
    huggingface_model: str = "Qwen/Qwen2.5-VL-72B-Instruct"
    google_drive_folder_id: str
    google_oauth_client_secret_file: str = "client_secret.json"
    google_oauth_token_file: str = "token.json"
    log_level: str = "INFO"

    model_config = {"env_file": ".env"}


settings = Settings()
