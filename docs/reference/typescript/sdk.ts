export class NexusClient {
  constructor(private apiKey: string, private baseUrl = "https://api.nexusai.com") {}

  async chat(prompt: string, mode = "chat") {
    const r = await fetch(`${this.baseUrl}/api/v1/nexus/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-API-Key": this.apiKey },
      body: JSON.stringify({ prompt, mode }),
    });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json();
  }
}
