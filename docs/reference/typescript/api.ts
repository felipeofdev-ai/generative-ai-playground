import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const api = axios.create({ baseURL: `${API_URL}/api/v1`, timeout: 60_000 });

export const nexusApi = {
  chat: async (prompt: string, mode: string = "chat") => (await api.post("/nexus/chat", { prompt, mode })).data,
};

export default api;
