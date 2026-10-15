"""Minimale client voor de Ollama HTTP API (/api/chat), zonder streaming."""

import logging
import time
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434"


class LLMError(Exception):
    """Fout bij het aanroepen van het LLM: timeout, geen verbinding, HTTP-fout of onverwacht antwoord."""


@dataclass(frozen=True)
class ChatResult:
    """Resultaat van één aanroep, onafhankelijk van de backend."""

    content: str
    done_reason: str | None  # "stop" = klaar, "length" = afgekapt
    tokens_in: int | None
    tokens_out: int | None
    seconds: float  # gemeten door de client, van verzoek tot antwoord
    raw: dict  # het volledige antwoord van de backend, voor logging


def chat(
    model: str,
    messages: list[dict[str, str]],
    options: dict | None = None,
    *,
    timeout: float = 120.0,
    base_url: str = OLLAMA_URL,
    client: httpx.Client | None = None,
) -> ChatResult:
    """Stuur messages naar Ollama en geef het antwoord terug als ChatResult.

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
    start = time.perf_counter()
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
    seconds = time.perf_counter() - start

    message = data.get("message")
    if not isinstance(message, dict) or "content" not in message:
        raise LLMError(f"Onverwacht antwoord, geen message.content: {data}")

    result = ChatResult(
        content=message["content"],
        done_reason=data.get("done_reason"),
        tokens_in=data.get("prompt_eval_count"),
        tokens_out=data.get("eval_count"),
        seconds=seconds,
        raw=data,
    )
    logger.info(
        "model=%s tokens_in=%s tokens_uit=%s duur=%.2fs done_reason=%s",
        model, result.tokens_in, result.tokens_out, result.seconds, result.done_reason,
    )
    if result.done_reason == "length":
        logger.warning("Antwoord afgekapt door num_predict (done_reason=length)")
    if message.get("thinking"):
        logger.warning("Model heeft gedacht ondanks think=false")
    return result
