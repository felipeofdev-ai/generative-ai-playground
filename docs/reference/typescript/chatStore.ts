import { create } from "zustand";
import { nexusApi } from "./api";

type Msg = { role: "user" | "assistant"; content: string };

type State = {
  messages: Msg[];
  sendMessage: (content: string) => Promise<void>;
};

export const useChatStore = create<State>((set, get) => ({
  messages: [],
  sendMessage: async (content) => {
    set({ messages: [...get().messages, { role: "user", content }] });
    const data = await nexusApi.chat(content);
    set({ messages: [...get().messages, { role: "assistant", content: data.response ?? "" }] });
  },
}));
