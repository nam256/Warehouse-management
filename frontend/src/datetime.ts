/** Định dạng thời gian API (UTC) sang giờ Việt Nam */

export function parseApiUtc(iso: string): Date {
  if (!iso) return new Date(NaN);
  const hasTz = iso.endsWith("Z") || /[+-]\d{2}:\d{2}$/.test(iso);
  return new Date(hasTz ? iso : `${iso}Z`);
}

export function formatVnDateTime(iso: string): string {
  const d = parseApiUtc(iso);
  if (Number.isNaN(d.getTime())) return iso.slice(0, 19);
  return d.toLocaleString("vi-VN", {
    timeZone: "Asia/Ho_Chi_Minh",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export function todayVn(): string {
  return new Date().toLocaleDateString("sv-SE", { timeZone: "Asia/Ho_Chi_Minh" });
}
