class ChatRepository:
    def save_message(self, tenant_id: str, session_id: str, role: str, content: str) -> dict:
        return {"tenant_id": tenant_id, "session_id": session_id, "role": role, "content": content}
