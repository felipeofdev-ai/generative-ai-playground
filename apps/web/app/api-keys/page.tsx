"use client";
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiKeys } from "@/lib/api";

export default function APIKeysPage() {
  const queryClient = useQueryClient();
  const [newKeyName, setNewKeyName] = useState("");
  const [rateLimit, setRateLimit] = useState(60);

  const { data } = useQuery({ queryKey: ["api-keys"], queryFn: () => apiKeys.list() });

  const createMutation = useMutation({
    mutationFn: () => apiKeys.create({ name: newKeyName, rate_limit_rpm: rateLimit }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["api-keys"] });
      setNewKeyName("");
    },
  });

  return (
    <main className="card">
      <h1>API Keys</h1>
      <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        <input value={newKeyName} onChange={(e) => setNewKeyName(e.target.value)} placeholder="Key name" />
        <input type="number" value={rateLimit} onChange={(e) => setRateLimit(parseInt(e.target.value || "0", 10))} />
        <button onClick={() => createMutation.mutate()}>Create key</button>
      </div>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </main>
  );
}
