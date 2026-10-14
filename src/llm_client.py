"""Minimale client voor de Ollama HTTP API (/api/chat), zonder streaming."""

import logging

import httpx

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434"


class LLMError(Exception):
    """Fout bij het aanroepen van het LLM: timeout, geen verbinding, HTTP-fout of onverwacht antwoord."""


def chat(
    model: str,
    messages: list[dict[str, str]],
    options: dict | None = None,
    *,
    timeout: float = 120.0,
    base_url: str = OLLAMA_URL,
    client: httpx.Client | None = None,
) -> dict:
    """Stuur messages naar Ollama en geef het volledige JSON-antwoord terug als dict.

    `client` is bedoeld voor tests (nep-server); normaal laat je hem leeg.
    """
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "think": False,
        "options": options or {},
    }
    http = client or httpx.Client(base_url=base_url, timeout=timeout)
    try:
        response = http.post("/api/chat", json=payload)
        response.raise_for_status()
        data = response.json()
    except httpx.TimeoutException as e:
        raise LLMError(f"Timeout na {timeout} s (koude start? model te groot?)") from e
    except httpx.ConnectError as e:
        raise LLMError(f"Geen verbinding met Ollama op {base_url}; draait de server?") from e
    except httpx.HTTPStatusError as e:
        raise LLMError(f"HTTP {e.response.status_code}: {e.response.text}") from e
    except ValueError as e:
        raise LLMError("Antwoord is geen geldige JSON (stream per ongeluk aan?)") from e
    finally:
        if client is None:
            http.close()

    message = data.get("message")
    if not isinstance(message, dict) or "content" not in message:
        raise LLMError(f"Onverwacht antwoord, geen message.content: {data}")

    logger.info(
        "model=%s tokens_in=%s tokens_uit=%s duur=%.1fs done_reason=%s",
        model,
        data.get("prompt_eval_count"),
        data.get("eval_count"),
        data.get("total_duration", 0) / 1e9,
        data.get("done_reason"),
    )
    if data.get("done_reason") == "length":
        logger.warning("Antwoord afgekapt door num_predict (done_reason=length)")
    if message.get("thinking"):
        logger.warning("Model heeft gedacht ondanks think=false")
    return data
