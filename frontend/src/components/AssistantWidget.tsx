import { useCallback, useEffect, useRef, useState } from "react";
import type { FormEvent, KeyboardEvent, PointerEvent as ReactPointerEvent } from "react";

import {
  ASK_TIMEOUT_MS,
  clearAssistantThread,
  loadAssistantThread,
  saveAssistantThread,
  type StoredChatMessage,
} from "../assistantThread";
import {
  askAssistant,
  getAssistantStatus,
  type AssistantStatus,
} from "../api";
import AlertBanner from "./ui/AlertBanner";

const TOOL_LABELS: Record<string, string> = {
  get_inventory: "Tồn kho",
  get_batch_status: "Trạng thái lô",
  list_expiring_batches: "Hạn dùng / FEFO",
  list_open_capa: "Hành động khắc phục đang mở",
  simulate_recall: "Mô phỏng thu hồi",
  explain_stock_reports: "Hướng dẫn báo cáo xuất/tồn",
  list_stock_issues: "Phiếu xuất gần đây",
};

const SUGGESTION_GROUPS: { title: string; items: { label: string; question: string }[] }[] = [
  {
    title: "Báo cáo & xuất kho",
    items: [
      { label: "In phiếu PX", question: "Làm sao in phiếu xuất kho?" },
      { label: "Sổ xuất", question: "Sổ xuất kho lọc ngày ra sao?" },
      { label: "Tồn theo kỳ", question: "Báo cáo tồn kho theo kỳ tính tồn đầu nhập xuất tồn cuối ra sao?" },
      { label: "Khả dụng", question: "Tồn khả dụng khác tồn vật lý thế nào? Lô cách ly có xuất được không?" },
      { label: "Xuất tay / mẻ", question: "Xuất tay khác xuất cho mẻ sản xuất thế nào trên phiếu PX?" },
      { label: "Phiếu nhập", question: "Phiếu nhập lấy kg lúc nhập hay tồn hiện tại?" },
      { label: "Vượt khả dụng", question: "Xuất vượt khả dụng thì sao?" },
      { label: "File và màn hình", question: "Tồn trên file khác màn hình không?" },
      { label: "Nhiều lô một lần", question: "Xuất nhiều lô một lần thì sao?" },
      { label: "Chỉ đọc", question: "Trợ lý có được xuất kho / duyệt lô không?" },
    ],
  },
  {
    title: "Vận hành",
    items: [
      { label: "Tồn kho", question: "Tồn kho còn bao nhiêu?" },
      { label: "Hạn dùng", question: "Lô nào sắp hết hạn?" },
      { label: "Khắc phục đang mở", question: "Có hành động khắc phục nào đang mở?" },
      { label: "Nhập kho", question: "Làm sao nhập kho?" },
      { label: "Sản xuất", question: "Làm sao tạo mẻ và bắt đầu sản xuất?" },
      { label: "Kiểm nghiệm", question: "Kiểm nghiệm Lab xong thì xuất được chưa?" },
      { label: "Giải phóng lô", question: "Phê duyệt chất lượng ATTP làm gì?" },
      { label: "Tồn thấp", question: "Cảnh báo tồn thấp so với số nào?" },
      { label: "Mua hàng", question: "Yêu cầu mua hàng dùng khi nào?" },
      { label: "Điểm kiểm soát", question: "Giám sát điểm kiểm soát HACCP in ở đâu?" },
      { label: "Nhật ký", question: "Nhật ký thao tác ghi ai xuất không?" },
      { label: "NVL / BTP / TP", question: "Thành phẩm xuất khác nguyên liệu không?" },
    ],
  },
  {
    title: "Trợ lý",
    items: [
      { label: "Chat có mất không", question: "Tắt khung chat có mất không?" },
      { label: "Không phải kế toán", question: "Đây có phải báo cáo kế toán không?" },
    ],
  },
];

const FALLBACK_STATUS: AssistantStatus = {
  enabled: false,
  available: false,
  provider: "none",
  message: "Không tải được trạng thái trợ lý.",
};

type ChatMessage = StoredChatMessage;
type WidgetPos = { right: number; bottom: number };
type WidgetSize = { w: number; h: number };

const POS_KEY = "oxeyns.assistant.pos";
const SIZE_KEY = "oxeyns.assistant.size.v4";
const MARGIN = 8;
const MIN_W = 320;
const MIN_H = 400;
const MAX_W = 560;
const MAX_H = 640;
const DEFAULT_SIZE: WidgetSize = { w: 400, h: 520 };

function readSavedPos(): WidgetPos | null {
  try {
    const raw = localStorage.getItem(POS_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as WidgetPos;
    if (typeof parsed.right !== "number" || typeof parsed.bottom !== "number") return null;
    return parsed;
  } catch {
    return null;
  }
}

function clampPos(pos: WidgetPos, width: number, height: number): WidgetPos {
  const maxRight = Math.max(MARGIN, window.innerWidth - width - MARGIN);
  const maxBottom = Math.max(MARGIN, window.innerHeight - height - MARGIN);
  return {
    right: Math.min(maxRight, Math.max(MARGIN, pos.right)),
    bottom: Math.min(maxBottom, Math.max(MARGIN, pos.bottom)),
  };
}

function readSavedSize(): WidgetSize | null {
  try {
    const raw = localStorage.getItem(SIZE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as WidgetSize;
    if (typeof parsed.w !== "number" || typeof parsed.h !== "number") return null;
    return parsed;
  } catch {
    return null;
  }
}

function isPhoneViewport() {
  return window.matchMedia("(max-width: 720px)").matches;
}

function clampSize(size: WidgetSize): WidgetSize {
  if (isPhoneViewport()) {
    return { w: 272, h: 236 };
  }
  const maxW = Math.min(MAX_W, Math.max(MIN_W, window.innerWidth - MARGIN * 2));
  const maxH = Math.min(MAX_H, Math.max(MIN_H, window.innerHeight - MARGIN * 2));
  return {
    w: Math.min(maxW, Math.max(MIN_W, size.w)),
    h: Math.min(maxH, Math.max(MIN_H, size.h)),
  };
}

type Props = { username: string };

export default function AssistantWidget({ username }: Props) {
  const [open, setOpen] = useState(false);
  const [status, setStatus] = useState<AssistantStatus | null>(null);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>(() => loadAssistantThread(username));
  const [busy, setBusy] = useState(false);
  const [confirmNew, setConfirmNew] = useState(false);
  const [pos, setPos] = useState<WidgetPos | null>(() => readSavedPos());
  const [size, setSize] = useState<WidgetSize>(() => clampSize(readSavedSize() ?? DEFAULT_SIZE));
  const [phone, setPhone] = useState(() => isPhoneViewport());
  const [dragging, setDragging] = useState(false);
  const [resizing, setResizing] = useState(false);
  const bodyRef = useRef<HTMLDivElement>(null);
  const widgetRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);
  const dragRef = useRef<{
    pointerId: number;
    startX: number;
    startY: number;
    startRight: number;
    startBottom: number;
    moved: boolean;
  } | null>(null);
  const skipClickRef = useRef(false);
  const resizeRef = useRef<{
    pointerId: number;
    startX: number;
    startY: number;
    startW: number;
    startH: number;
    startRight: number;
    startBottom: number;
  } | null>(null);

  useEffect(() => {
    setMessages(loadAssistantThread(username));
  }, [username]);

  useEffect(() => {
    saveAssistantThread(username, messages);
  }, [username, messages]);

  useEffect(() => {
    let active = true;
    async function loadStatus() {
      try {
        const nextStatus = await getAssistantStatus();
        if (active) setStatus(nextStatus);
      } catch {
        if (active) setStatus(FALLBACK_STATUS);
      }
    }
    void loadStatus();
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (!bodyRef.current) return;
    bodyRef.current.scrollTop = bodyRef.current.scrollHeight;
  }, [messages, busy, open]);

  const persistSize = useCallback((next: WidgetSize) => {
    const clamped = clampSize(next);
    setSize(clamped);
    if (isPhoneViewport()) return;
    try {
      localStorage.setItem(SIZE_KEY, JSON.stringify(clamped));
    } catch {
      /* ignore quota */
    }
  }, []);

  const persistPos = useCallback((next: WidgetPos, boxSize?: WidgetSize) => {
    const w = boxSize?.w ?? size.w;
    const h = boxSize?.h ?? size.h;
    const clamped = clampPos(next, open ? w : 56, open ? h : 56);
    setPos(clamped);
    if (isPhoneViewport()) return;
    try {
      localStorage.setItem(POS_KEY, JSON.stringify(clamped));
    } catch {
      /* ignore quota */
    }
  }, [open, size.h, size.w]);

  useEffect(() => {
    if (!pos || !widgetRef.current) return;
    persistPos(pos);
  }, [open]); // eslint-disable-line react-hooks/exhaustive-deps -- clamp after panel opens/closes

  useEffect(() => {
    const media = window.matchMedia("(max-width: 720px)");
    const sync = () => setPhone(media.matches);
    sync();
    media.addEventListener("change", sync);
    return () => media.removeEventListener("change", sync);
  }, []);

  function startResize(event: ReactPointerEvent<HTMLButtonElement>) {
    if (event.button !== 0) return;
    event.stopPropagation();
    event.preventDefault();
    const box = widgetRef.current;
    const rect = box?.getBoundingClientRect();
    resizeRef.current = {
      pointerId: event.pointerId,
      startX: event.clientX,
      startY: event.clientY,
      startW: size.w,
      startH: size.h,
      startRight: rect ? window.innerWidth - rect.right : pos?.right ?? MARGIN,
      startBottom: rect ? window.innerHeight - rect.bottom : pos?.bottom ?? MARGIN,
    };
    event.currentTarget.setPointerCapture(event.pointerId);
    setResizing(true);
  }

  function onResizeMove(event: ReactPointerEvent<HTMLButtonElement>) {
    const drag = resizeRef.current;
    if (!drag || drag.pointerId !== event.pointerId) return;
    const dx = event.clientX - drag.startX;
    const dy = event.clientY - drag.startY;
    const nextSize = clampSize({ w: drag.startW + dx, h: drag.startH + dy });
    persistSize(nextSize);
    persistPos(
      {
        right: drag.startRight - (nextSize.w - drag.startW),
        bottom: drag.startBottom - (nextSize.h - drag.startH),
      },
      nextSize,
    );
  }

  function endResize(event: ReactPointerEvent<HTMLButtonElement>) {
    const drag = resizeRef.current;
    if (!drag || drag.pointerId !== event.pointerId) return;
    try {
      event.currentTarget.releasePointerCapture(event.pointerId);
    } catch {
      /* already released */
    }
    resizeRef.current = null;
    setResizing(false);
  }

  function startDrag(event: ReactPointerEvent<HTMLElement>) {
    if (phone) return;
    if (event.button !== 0) return;
    if ((event.target as HTMLElement).closest("button")) return;
    const box = widgetRef.current;
    if (!box) return;
    const rect = box.getBoundingClientRect();
    dragRef.current = {
      pointerId: event.pointerId,
      startX: event.clientX,
      startY: event.clientY,
      startRight: window.innerWidth - rect.right,
      startBottom: window.innerHeight - rect.bottom,
      moved: false,
    };
    event.currentTarget.setPointerCapture(event.pointerId);
    setDragging(true);
  }

  function onDragMove(event: ReactPointerEvent<HTMLElement>) {
    const drag = dragRef.current;
    const box = widgetRef.current;
    if (!drag || drag.pointerId !== event.pointerId || !box) return;
    const dx = event.clientX - drag.startX;
    const dy = event.clientY - drag.startY;
    if (Math.abs(dx) > 4 || Math.abs(dy) > 4) drag.moved = true;
    persistPos({
      right: drag.startRight - dx,
      bottom: drag.startBottom - dy,
    });
  }

  function endDrag(event: ReactPointerEvent<HTMLElement>) {
    const drag = dragRef.current;
    if (!drag || drag.pointerId !== event.pointerId) return;
    try {
      event.currentTarget.releasePointerCapture(event.pointerId);
    } catch {
      /* already released */
    }
    if (drag.moved) skipClickRef.current = true;
    dragRef.current = null;
    setDragging(false);
  }

  function toggleOpen() {
    if (skipClickRef.current) {
      skipClickRef.current = false;
      return;
    }
    setOpen((current) => !current);
  }

  function cancelAsk() {
    abortRef.current?.abort();
  }

  function requestNewChat() {
    if (messages.length === 0 && !busy) return;
    setConfirmNew(true);
  }

  function confirmNewChat() {
    abortRef.current?.abort();
    setMessages([]);
    clearAssistantThread(username);
    setBusy(false);
    setConfirmNew(false);
  }

  async function ask(trimmed: string) {
    if (!trimmed || busy) return;
    setConfirmNew(false);
    setBusy(true);
    setQuestion("");
    const userMsg: ChatMessage = { id: `u-${Date.now()}`, role: "user", text: trimmed };
    setMessages((current) => [...current, userMsg]);

    const controller = new AbortController();
    abortRef.current = controller;
    const timer = window.setTimeout(() => controller.abort(), ASK_TIMEOUT_MS);
    try {
      const answer = await askAssistant(trimmed, { signal: controller.signal });
      setMessages((current) => [
        ...current,
        {
          id: `a-${Date.now()}`,
          role: "assistant",
          text: answer.answer,
          tools: answer.tools_called,
        },
      ]);
    } catch (caught) {
      const aborted = controller.signal.aborted;
      const text = aborted
        ? "Hết giờ hoặc đã hủy. Tin nhắn vẫn còn — gửi lại giúp."
        : caught instanceof Error
          ? caught.message
          : "Trợ lý tạm thời không khả dụng.";
      setMessages((current) => [
        ...current,
        { id: `a-err-${Date.now()}`, role: "assistant", text },
      ]);
    } finally {
      window.clearTimeout(timer);
      if (abortRef.current === controller) abortRef.current = null;
      setBusy(false);
    }
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await ask(question.trim());
  }

  function onKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void ask(question.trim());
    }
  }

  const isAvailable = status?.available === true;
  const buttonLabel = isAvailable ? "Mở trợ lý AI" : "Trợ lý AI chưa khả dụng";
  const dragHandlers = {
    onPointerDown: startDrag,
    onPointerMove: onDragMove,
    onPointerUp: endDrag,
    onPointerCancel: endDrag,
  };

  return (
    <div
      ref={widgetRef}
      className={`assistant-widget${phone ? " assistant-widget--phone" : ""}${open ? " assistant-widget--open" : ""}${dragging ? " assistant-widget--dragging" : ""}${resizing ? " assistant-widget--resizing" : ""}`}
      style={phone ? { right: 10, bottom: 10 } : pos ? { right: pos.right, bottom: pos.bottom } : undefined}
    >
      {open ? (
        <section
          className={`assistant-panel${messages.length > 0 ? " assistant-panel--chatting" : ""}`}
          role="dialog"
          aria-label="Trợ lý AI chỉ đọc"
          style={phone ? undefined : { width: size.w, height: size.h }}
        >
          <header
            className="assistant-panel__header"
            title={phone ? undefined : "Kéo để di chuyển"}
            {...(phone ? {} : dragHandlers)}
          >
            <div className="assistant-panel__brand">
              <span className="assistant-panel__avatar" aria-hidden="true">
                AI
              </span>
              <div>
                <strong>Trợ lý</strong>
                <span className="assistant-panel__badge">Chỉ đọc</span>
              </div>
            </div>
            <div className="assistant-panel__toolbar">
              <button
                type="button"
                className="assistant-panel__new"
                onClick={requestNewChat}
                onPointerDown={(event) => event.stopPropagation()}
                disabled={messages.length === 0 && !busy}
              >
                Mới
              </button>
              <button
                type="button"
                className="assistant-panel__close"
                onClick={() => setOpen(false)}
                onPointerDown={(event) => event.stopPropagation()}
                aria-label="Thu gọn trợ lý"
              >
                ×
              </button>
            </div>
          </header>

          {confirmNew ? (
            <div className="assistant-confirm">
              <p>Xóa chat này?</p>
              <button type="button" onClick={confirmNewChat}>
                Xóa
              </button>
              <button type="button" className="assistant-confirm__ghost" onClick={() => setConfirmNew(false)}>
                Không
              </button>
            </div>
          ) : null}

          <div className="assistant-panel__body" ref={bodyRef}>
            {status && !isAvailable ? (
              <AlertBanner tone="warning">{status.message}</AlertBanner>
            ) : null}

            {messages.length === 0 && isAvailable ? (
              <p className="assistant-hint">
                {phone
                  ? "Bấm gợi ý hoặc gõ câu hỏi."
                  : "Bấm gợi ý hoặc gõ câu hỏi. Kéo thanh trên để dời khung, góc dưới-phải để đổi cỡ."}
              </p>
            ) : null}

            <div className="assistant-thread" aria-live="polite">
              {messages.map((message) => (
                <article
                  key={message.id}
                  className={`assistant-bubble assistant-bubble--${message.role}`}
                >
                  <p>{message.text}</p>
                  {message.role === "assistant" && message.tools && message.tools.length > 0 ? (
                    <div className="assistant-sources">
                      <span>Nguồn</span>
                      <ul>
                        {message.tools.map((tool, index) => (
                          <li key={`${message.id}-${tool}-${index}`}>{TOOL_LABELS[tool] ?? tool}</li>
                        ))}
                      </ul>
                    </div>
                  ) : null}
                </article>
              ))}
              {busy ? (
                <article className="assistant-bubble assistant-bubble--assistant assistant-bubble--typing">
                  <span />
                  <span />
                  <span />
                </article>
              ) : null}
            </div>
          </div>

          <form className="assistant-form" onSubmit={onSubmit}>
            {phone && messages.length > 0 ? null : (
            <div className="assistant-suggestions">
              {SUGGESTION_GROUPS.map((group) => (
                <div key={group.title} className="assistant-suggest-group">
                  <p className="assistant-suggest-group__title">{group.title}</p>
                  {group.items.map((item) => (
                    <button
                      key={item.question}
                      type="button"
                      className="assistant-suggestion"
                      disabled={busy}
                      onClick={() => void ask(item.question)}
                    >
                      {item.label}
                    </button>
                  ))}
                </div>
              ))}
            </div>
            )}
            <label className="sr-only" htmlFor="assistant-question">
              Câu hỏi
            </label>
            <div className="assistant-composer">
              <textarea
                id="assistant-question"
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                onKeyDown={onKeyDown}
                placeholder="Nhập câu hỏi…"
                rows={phone ? 1 : 2}
                maxLength={2000}
                disabled={busy}
              />
              {busy ? (
                <button type="button" className="assistant-send assistant-send--cancel" onClick={cancelAsk} aria-label="Hủy">
                  ✕
                </button>
              ) : (
                <button
                  type="submit"
                  className="assistant-send"
                  disabled={!question.trim()}
                  aria-label="Gửi câu hỏi"
                >
                  ↑
                </button>
              )}
            </div>
          </form>
          {phone ? null : (
          <button
            type="button"
            className="assistant-resize"
            aria-label="Kéo góc để đổi cỡ"
            title="Kéo góc dưới-phải để đổi cỡ"
            onPointerDown={startResize}
            onPointerMove={onResizeMove}
            onPointerUp={endResize}
            onPointerCancel={endResize}
          />
          )}
        </section>
      ) : null}

      <button
        type="button"
        className="assistant-toggle"
        onClick={toggleOpen}
        aria-expanded={open}
        aria-label={buttonLabel}
        title={phone ? (status?.message ?? "Trợ lý") : `${status?.message ?? "Đang kiểm tra trạng thái trợ lý..."} — kéo để di chuyển`}
        {...(phone ? {} : dragHandlers)}
      >
        {open ? "×" : "AI"}
        {!isAvailable && status ? <span aria-hidden="true">!</span> : null}
      </button>
    </div>
  );
}
