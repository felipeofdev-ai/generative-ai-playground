"""NexusAI Python SDK (reference)."""
import httpx

class NexusClient:
    def __init__(self, api_key: str, base_url: str = "https://api.nexusai.com"):
        self._client = httpx.Client(base_url=f"{base_url.rstrip('/')}/api/v1", headers={"X-API-Key": api_key})

    def chat(self, prompt: str, mode: str = "chat") -> dict:
        r = self._client.post("/nexus/chat", json={"prompt": prompt, "mode": mode})
        r.raise_for_status()
        return r.json()
