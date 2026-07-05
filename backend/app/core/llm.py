import os
from dotenv import load_dotenv

load_dotenv()

_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()

_PROVIDER_MAP = {
    "gemini": ("GEMINI_API_KEY", "GEMINI_MODEL", "gemini-2.0-flash"),
    "openai": ("OPENAI_API_KEY", "OPENAI_MODEL", "gpt-4o-mini"),
    "claude": ("ANTHROPIC_API_KEY", "ANTHROPIC_MODEL", "claude-3-5-haiku-20241022"),
}


def get_model():
    """Return a LangGraph-compatible chat model based on LLM_PROVIDER in .env."""
    if _PROVIDER not in _PROVIDER_MAP:
        raise ValueError(f"Unsupported LLM_PROVIDER '{_PROVIDER}'. Choose: gemini | openai | claude")

    key_env, model_env, default_model = _PROVIDER_MAP[_PROVIDER]
    model_name = os.getenv(model_env, default_model)
    api_key = os.getenv(key_env)

    if _PROVIDER == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=model_name, api_key=api_key,temperature=0)

    if _PROVIDER == "claude":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=model_name, api_key=api_key,temperature=0)

    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key,temperature=0)
