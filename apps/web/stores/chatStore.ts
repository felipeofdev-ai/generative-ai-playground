import { create } from "zustand";

type ChatState = {
  messages: string[];
  addMessage: (msg: string) => void;
};

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),
}));
