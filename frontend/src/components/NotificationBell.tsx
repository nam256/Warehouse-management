import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { pingAlert, unlockAlertSound } from "../alertSound";
import { getAlerts, type AlertItem } from "../api";

const POLL_MS = 60_000;
const SEEN_KEY = "oxeyns-alerts-seen.v2";

const KIND_LABEL: Record<string, string> = {
  out_of_stock: "Hết hàng",
  low_stock: "Tồn thấp",
  expired: "Hết hạn",
  expiring_soon: "Sắp hết hạn",
  quality_fail: "Không đạt",
  awaiting_release: "Chờ giải phóng",
  ccp2_fail: "CCP2",
  capa_overdue: "Khắc phục quá hạn",
  capa_due_soon: "Khắc phục sắp hạn",
  purchase_pending: "Yêu cầu mua",
};

function kindLabel(kind: string): string {
  return KIND_LABEL[kind] ?? "Cảnh báo";
}

function loadSeen(): Set<string> {
  try {
    const raw = localStorage.getItem(SEEN_KEY);
    if (!raw) return new Set();
    const parsed = JSON.parse(raw) as string[];
    return new Set(Array.isArray(parsed) ? parsed : []);
  } catch {
    return new Set();
  }
}

function saveSeen(ids: Set<string>) {
  localStorage.setItem(SEEN_KEY, JSON.stringify([...ids].slice(-200)));
}

export default function NotificationBell() {
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [items, setItems] = useState<AlertItem[]>([]);
  const [toast, setToast] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [seenTick, setSeenTick] = useState(0);
  const [ringing, setRinging] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);
  const seenRef = useRef<Set<string>>(loadSeen());
  const firstLoad = useRef(true);

  const refresh = useCallback(async () => {
    try {
      const feed = await getAlerts();
      const next = feed.items ?? [];
      setItems(next);
      setError(null);

      const unseen = next.filter((item) => !seenRef.current.has(item.id));
      if (!firstLoad.current && unseen.length > 0) {
        const sample = unseen[0];
        setToast(
          unseen.length === 1
            ? sample.title
            : `${unseen.length} cảnh báo mới — ${sample.title}`,
        );
        pingAlert();
        setRinging(true);
      }
      firstLoad.current = false;

      const currentIds = new Set(next.map((item) => item.id));
      // Giữ seen cho id còn hiệu lực; id mới chưa đánh dấu cho đến khi mở panel
      const pruned = new Set([...seenRef.current].filter((id) => currentIds.has(id)));
      seenRef.current = pruned;
      saveSeen(pruned);
    } catch {
      setError("Không tải được cảnh báo");
    }
  }, []);

  useEffect(() => {
    void refresh();
    const timer = window.setInterval(() => void refresh(), POLL_MS);
    const onFocus = () => void refresh();
    window.addEventListener("focus", onFocus);
    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "visible") void refresh();
    });
    return () => {
      window.clearInterval(timer);
      window.removeEventListener("focus", onFocus);
    };
  }, [refresh]);

  useEffect(() => {
    if (!toast) return;
    const timer = window.setTimeout(() => setToast(null), 4500);
    return () => window.clearTimeout(timer);
  }, [toast]);

  useEffect(() => {
    if (!ringing) return;
    const timer = window.setTimeout(() => setRinging(false), 800);
    return () => window.clearTimeout(timer);
  }, [ringing]);

  useEffect(() => {
    if (!open) return;
    const onPointer = (event: MouseEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false);
    };
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };
    window.addEventListener("mousedown", onPointer);
    window.addEventListener("keydown", onKey);
    return () => {
      window.removeEventListener("mousedown", onPointer);
      window.removeEventListener("keydown", onKey);
    };
  }, [open]);

  function markAllSeen() {
    const next = new Set(items.map((item) => item.id));
    seenRef.current = next;
    saveSeen(next);
    setSeenTick((value) => value + 1);
  }

  function toggleOpen() {
    unlockAlertSound();
    setOpen((prev) => {
      const next = !prev;
      if (next) markAllSeen();
      return next;
    });
  }

  function openAlert(item: AlertItem) {
    seenRef.current.add(item.id);
    saveSeen(seenRef.current);
    setSeenTick((value) => value + 1);
    setOpen(false);
    navigate(item.href);
  }

  const unread = items.filter((item) => !seenRef.current.has(item.id)).length;
  const hasUnread = unread > 0;
  const badgeCount = items.length;
  void seenTick;

  return (
    <div className="notify" ref={rootRef}>
      <button
        type="button"
        className={`notify__bell${items.length ? " notify__bell--active" : ""}${hasUnread ? " notify__bell--unread" : ""}${ringing ? " notify__bell--ring" : ""}`}
        aria-label={items.length ? `${items.length} cảnh báo${unread ? `, ${unread} chưa xem` : ""}` : "Không có cảnh báo"}
        aria-expanded={open}
        aria-haspopup="dialog"
        onClick={toggleOpen}
      >
        <svg className="notify__icon" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
          <path
            fill="currentColor"
            d="M12 22a2.4 2.4 0 0 0 2.4-2.4h-4.8A2.4 2.4 0 0 0 12 22Zm8-6.5V11a8 8 0 1 0-16 0v4.5L2 18.2V20h20v-1.8L20 15.5Z"
          />
        </svg>
        {items.length > 0 && (
          <span className="notify__badge">{badgeCount > 99 ? "99+" : badgeCount}</span>
        )}
      </button>

      {open && (
        <div className="notify__panel" role="dialog" aria-label="Danh sách cảnh báo">
          <header className="notify__header">
            <div>
              <strong>Cảnh báo</strong>
              <p className="notify__scope">Hết hàng · hạn dùng · giải phóng · CCP · khắc phục · mua hàng</p>
            </div>
            <button type="button" className="secondary" onClick={() => void refresh()}>
              Làm mới
            </button>
          </header>
          {error && <p className="notify__empty">{error}</p>}
          {!error && items.length === 0 && (
            <p className="notify__empty">Không có cảnh báo — kho và chất lượng ổn định.</p>
          )}
          {!error && items.length > 0 && (
            <ul className="notify__list">
              {items.map((item) => (
                <li key={item.id}>
                  <button
                    type="button"
                    className={`notify__item notify__item--${item.severity}`}
                    onClick={() => openAlert(item)}
                  >
                    <span className="notify__kind">{kindLabel(item.kind)}</span>
                    <strong>{item.title}</strong>
                    <span>{item.detail}</span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {toast && (
        <div className="notify__toast" role="status" aria-live="polite">
          {toast}
        </div>
      )}
    </div>
  );
}
