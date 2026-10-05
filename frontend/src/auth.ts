/** Kiểm tra JWT lưu trong trình duyệt — tránh gọi API khi token đã hết hạn */

export function readStoredToken(): string | null {
  const token = localStorage.getItem("token");
  if (!token || token === "null" || token === "undefined") return null;
  return token;
}

export function isStoredTokenValid(): boolean {
  const token = readStoredToken();
  if (!token) return false;
  try {
    const part = token.split(".")[1];
    if (!part) return false;
    const payload = JSON.parse(atob(part.replace(/-/g, "+").replace(/_/g, "/"))) as { exp?: number };
    if (!payload.exp) return false;
    return payload.exp * 1000 > Date.now();
  } catch {
    return false;
  }
}

export function clearStoredToken(): void {
  localStorage.removeItem("token");
}

export function saveStoredToken(token: string): void {
  localStorage.setItem("token", token);
}
