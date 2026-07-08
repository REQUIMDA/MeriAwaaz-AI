"""
Submission decomposition
-------------------------
A single citizen message can raise SEVERAL unrelated problems, e.g.:

    "Kesarpur has too many road potholes and its health center has a
     shortage of medical supplies."

That is really two demands — one Roads issue and one Healthcare issue — and each
should feed its OWN demand cluster / project. This module splits a raw
submission into a list of distinct, self-contained single-topic complaints.

Design notes:
- Pure language task → uses the configured LLM (get_model()).
- Deterministic-degradation: if the LLM is unavailable or returns anything
  unparseable, we fall back to a SINGLE issue == the original text, so behaviour
  is identical to the old single-topic pipeline. Splitting never breaks intake.
- Each returned string preserves the place name + specifics so it can be parsed
  and clustered independently by the existing pipeline.
"""
import json
import logging
import re

logger = logging.getLogger("pipeline")

_MAX_ISSUES = 6          # safety cap — never fan out to an unbounded number


def _strip_json(text: str) -> dict:
    text = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            return json.loads(m.group(0))
        raise


_PROMPT = (
    "You are triaging a citizen complaint sent to an Indian Member of Parliament.\n"
    "A single message may raise SEVERAL separate problems (for example bad roads "
    "AND a clinic medicine shortage — different topics, or the same topic in "
    "different places).\n\n"
    "Split the message into DISTINCT, self-contained complaints — ONE per real "
    "problem. Rules:\n"
    "- Each complaint must keep the place/ward/village name and the concrete "
    "details, so it can stand completely on its own.\n"
    "- Group sentences about the SAME problem together (do not over-split).\n"
    "- If the message is about only one problem, return exactly one item.\n"
    "- Never invent problems that are not in the message.\n\n"
    'Return ONLY JSON, no prose, no markdown:\n'
    '{"issues": ["<complaint 1>", "<complaint 2>"]}\n\n'
    'Message:\n"""%s"""'
)


def decompose_text(text: str) -> list[str]:
    """Return a list of 1..N single-topic complaint strings.

    Always returns at least one element when given non-empty text (the original
    text) so callers can loop uniformly. Returns [] only for empty input.
    """
    text = (text or "").strip()
    if not text:
        return []
    try:
        from app.core.llm import get_model, content_to_text
        from langchain_core.messages import HumanMessage

        resp = get_model().invoke([HumanMessage(content=_PROMPT % text)])
        content = content_to_text(getattr(resp, "content", resp))
        data = _strip_json(content)
        issues = [str(s).strip() for s in data.get("issues", []) if str(s).strip()]
        issues = issues[:_MAX_ISSUES]
        if not issues:
            return [text]
        logger.info("[decompose] split submission into %d issue(s)", len(issues))
        return issues
    except Exception as exc:
        # Any failure → behave exactly like the old single-topic pipeline.
        logger.warning("[decompose] single-issue fallback (%s)", exc)
        return [text]
