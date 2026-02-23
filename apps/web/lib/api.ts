const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080";

type InviteUserPayload = { email: string; full_name: string; role: string };
type CreateApiKeyPayload = { name: string; rate_limit_rpm: number };

async function request(path: string, init?: RequestInit) {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const users = {
  list: () => request("/api/v1/users"),
  invite: (payload: InviteUserPayload) => request("/api/v1/users/invite", { method: "POST", body: JSON.stringify(payload) }),
};

export const apiKeys = {
  list: () => request("/api/v1/api-keys"),
  create: (payload: CreateApiKeyPayload) => request("/api/v1/api-keys", { method: "POST", body: JSON.stringify(payload) }),
  revoke: (id: string) => request(`/api/v1/api-keys/${id}/revoke`, { method: "POST" }),
};
