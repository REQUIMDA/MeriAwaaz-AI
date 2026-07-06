from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gemini_api_key: str = ""          # still needed for embeddings + voice/video
    openai_api_key: str = ""
    openai_model: str = "gpt-5.5"
    llm_provider: str = "gemini"
    gemini_model: str = "gemini-3.5-flash"  # gemini-2.0-flash was shut down 2026-06-01
    database_url: str = "sqlite:///./data/meri_awaaz.db"
    chroma_path: str = "./data/chroma_db"
    env: str = "development"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()