"""Minimal client for a local Ollama server (no extra SDK needed)."""
import json
import requests
from src import config


def ollama_generate(prompt: str, system: str | None = None, temperature: float = 0.1) -> str:
    """Calls Ollama's /api/generate endpoint and returns the raw text response."""
    url = f"{config.OLLAMA_HOST}/api/generate"
    payload = {
        "model": config.OLLAMA_MODEL,
        "prompt": prompt,
        "system": system or "",
        "stream": False,
        "think": False,  # qwen3 supports a "thinking" mode; keep it off for speed/clean output
        "options": {"temperature": temperature},
    }
    resp = requests.post(url, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    return data.get("response", "").strip()


def check_ollama_alive() -> bool:
    try:
        r = requests.get(f"{config.OLLAMA_HOST}/api/tags", timeout=5)
        return r.status_code == 200
    except requests.RequestException:
        return False
