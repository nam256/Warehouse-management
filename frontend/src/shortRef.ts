/** SX-20260718-001 → SX-001. Mã vật tư kiểu NVL-QUE giữ nguyên. */
export function shortRef(code: string | null | undefined): string {
  if (!code) return "—";
  const parts = code.split("-");
  if (parts.length >= 3 && /^\d{8}$/.test(parts[1])) {
    return `${parts[0]}-${parts[parts.length - 1]}`;
  }
  return code;
}

export function refSeq(code: string | null | undefined): number {
  if (!code) return 0;
  const tail = code.split("-").pop() ?? "";
  const n = Number.parseInt(tail, 10);
  return Number.isFinite(n) ? n : 0;
}

export function sortByRef<T>(rows: T[], codeOf: (row: T) => string, idOf: (row: T) => number): T[] {
  return [...rows].sort((a, b) => {
    const seq = refSeq(codeOf(a)) - refSeq(codeOf(b));
    if (seq !== 0) return seq;
    return idOf(a) - idOf(b);
  });
}
