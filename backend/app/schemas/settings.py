from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    database_url: str = "sqlite:///./data/meri_awaaz.db"
    chroma_path: str = "./data/chroma_db"
    env: str = "development"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
