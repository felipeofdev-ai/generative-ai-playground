"use client";
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { users } from "@/lib/api";

export default function UsersPage() {
  const queryClient = useQueryClient();
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [role, setRole] = useState("viewer");

  const { data } = useQuery({ queryKey: ["users"], queryFn: () => users.list() });

  const inviteMutation = useMutation({
    mutationFn: () => users.invite({ email, full_name: name, role }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      setEmail("");
      setName("");
      setRole("viewer");
    },
  });

  return (
    <main className="card">
      <h1>Users & RBAC</h1>
      <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Name" />
        <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
        <select value={role} onChange={(e) => setRole(e.target.value)}>
          <option value="viewer">viewer</option>
          <option value="analyst">analyst</option>
          <option value="developer">developer</option>
          <option value="admin">admin</option>
        </select>
        <button onClick={() => inviteMutation.mutate()}>Invite</button>
      </div>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </main>
  );
}
