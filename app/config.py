from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    verosight_api_key: str = ""
    verosight_base_url: str = "https://api.verosight.com"
    embedding_model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
