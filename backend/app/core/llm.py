import os
from dotenv import load_dotenv

load_dotenv()

_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()

_PROVIDER_MAP = {
    "gemini": ("GEMINI_API_KEY", "GEMINI_MODEL", "gemini-3.5-flash"),
    "openai": ("OPENAI_API_KEY", "OPENAI_MODEL", "gpt-4o-mini"),
    "claude": ("ANTHROPIC_API_KEY", "ANTHROPIC_MODEL", "claude-3-5-haiku-20241022"),
}


def content_to_text(content) -> str:
    """Normalise a LangChain message's .content to plain text.

    Gemini 3.x models return content as a LIST of content blocks
    (e.g. [{"type": "text", "text": "..."}] or ["..."]) instead of the plain
    string that 2.x returned. Every parser downstream expects a string."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                text = block.get("text")
                if text:
                    parts.append(text)
        return "\n".join(parts)
    return str(content)


def get_model():
    """Return a LangGraph-compatible chat model based on LLM_PROVIDER in .env."""
    if _PROVIDER not in _PROVIDER_MAP:
        raise ValueError(f"Unsupported LLM_PROVIDER '{_PROVIDER}'. Choose: gemini | openai | claude")

    key_env, model_env, default_model = _PROVIDER_MAP[_PROVIDER]
    model_name = os.getenv(model_env, default_model)
    api_key = os.getenv(key_env)

    if _PROVIDER == "openai":
        from langchain_openai import ChatOpenAI
        kwargs = {"model": model_name, "api_key": api_key, "max_retries": 2}
        # GPT-5-family / o-series reasoning models reject custom temperature
        # values (only the default is allowed) — omit it for those.
        if not model_name.startswith(("gpt-5", "o1", "o3", "o4")):
            kwargs["temperature"] = 0
        return ChatOpenAI(**kwargs)

    if _PROVIDER == "claude":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=model_name, api_key=api_key,temperature=0)

    from langchain_google_genai import ChatGoogleGenerativeAI
    # max_retries=2: with the default (6+) a dead model/quota error made every
    # agent block ~35s before falling back (141s per doomed submission)
    return ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key,
                                  temperature=0, max_retries=2)
