const PREFIX = "oxeyns.assistant.thread.";

export const ASK_TIMEOUT_MS = 25_000;
export const THREAD_LIMIT = 50;

export type StoredChatMessage = {
  id: string;
  role: "user" | "assistant";
  text: string;
  tools?: string[];
};

export function assistantThreadKey(username: string): string {
  return `${PREFIX}${username}`;
}

export function loadAssistantThread(username: string): StoredChatMessage[] {
  try {
    const raw = localStorage.getItem(assistantThreadKey(username));
    if (!raw) return [];
    const parsed = JSON.parse(raw) as { messages?: StoredChatMessage[] };
    if (!Array.isArray(parsed.messages)) return [];
    return parsed.messages.filter(
      (row) =>
        row &&
        typeof row.id === "string" &&
        (row.role === "user" || row.role === "assistant") &&
        typeof row.text === "string",
    );
  } catch {
    return [];
  }
}

export function saveAssistantThread(username: string, messages: StoredChatMessage[]): void {
  try {
    localStorage.setItem(
      assistantThreadKey(username),
      JSON.stringify({ v: 1, messages: messages.slice(-THREAD_LIMIT), savedAt: Date.now() }),
    );
  } catch {
    /* quota */
  }
}

export function clearAssistantThread(username: string): void {
  try {
    localStorage.removeItem(assistantThreadKey(username));
  } catch {
    /* ignore */
  }
}
