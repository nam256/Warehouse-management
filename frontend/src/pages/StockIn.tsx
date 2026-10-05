import { useEffect, useMemo, useState } from "react";
import { createReceipt, getMaterials } from "../api";
import ProductThumb from "../components/ProductThumb";
import { LOAI_VAT_TU, nhan } from "../labels";
import AlertBanner from "../components/ui/AlertBanner";
import PageHeader from "../components/ui/PageHeader";
import StatusBadge from "../components/ui/StatusBadge";

type Material = {
  id: number;
  code: string;
  name: string;
  type?: string;
  unit?: string;
  image_url?: string | null;
};

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

function plusMonthsIso(months: number): string {
  const date = new Date();
  date.setMonth(date.getMonth() + months);
  return date.toISOString().slice(0, 10);
}

function formatVnDate(value: string): string {
  if (!value) return "—";
  return new Date(`${value}T00:00:00`).toLocaleDateString("vi-VN");
}

export default function StockIn() {
  const [materials, setMaterials] = useState<Material[]>([]);
  const [materialId, setMaterialId] = useState("");
  const [quantity, setQuantity] = useState("100");
  const [batchNo, setBatchNo] = useState("");
  const [mfgDate, setMfgDate] = useState(todayIso);
  const [expiryDate, setExpiryDate] = useState(() => plusMonthsIso(12));
  const [notes, setNotes] = useState("");
  const [msg, setMsg] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [tipsOpen, setTipsOpen] = useState(true);

  useEffect(() => {
    const media = window.matchMedia("(max-width: 720px)");
    const sync = () => setTipsOpen(!media.matches);
    sync();
    media.addEventListener("change", sync);
    return () => media.removeEventListener("change", sync);
  }, []);

  useEffect(() => {
    let active = true;

    async function loadMaterials() {
      setErr(null);
      setLoading(true);
      try {
        const result = (await getMaterials()) as Material[];
        if (!active) return;
        const sorted = [...result].sort((a, b) => {
          const rank = (type?: string) => (type === "NVL" ? 0 : type === "BTP" ? 1 : 2);
          return rank(a.type) - rank(b.type) || a.code.localeCompare(b.code);
        });
        setMaterials(sorted);
        const preferred = sorted.find((item) => item.type === "NVL") ?? sorted[0];
        if (preferred) setMaterialId(String(preferred.id));
      } catch (error) {
        if (!active) return;
        setErr(error instanceof Error ? error.message : "Không thể tải danh sách vật tư.");
      } finally {
        if (active) setLoading(false);
      }
    }

    void loadMaterials();
    return () => {
      active = false;
    };
  }, []);

  const selected = useMemo(
    () => materials.find((item) => String(item.id) === materialId) ?? null,
    [materials, materialId],
  );

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setMsg(null);
    setErr(null);

    if (!materialId) {
      setErr("Vui lòng chọn vật tư cần nhập.");
      return;
    }
    if (!expiryDate) {
      setErr("Vui lòng nhập hạn dùng của lô.");
      return;
    }
    if (mfgDate && expiryDate < mfgDate) {
      setErr("Hạn dùng phải sau ngày sản xuất.");
      return;
    }
    if (Number(quantity) <= 0) {
      setErr("Số lượng nhập phải lớn hơn 0.");
      return;
    }

    setBusy(true);
    try {
      const batch = await createReceipt({
        material_id: Number(materialId),
        quantity: Number(quantity),
        warehouse_id: 1,
        batch_no: batchNo.trim() || null,
        mfg_date: mfgDate || null,
        expiry_date: expiryDate,
        notes: notes.trim() || null,
      });
      setMsg(
        `Đã tạo phiếu nhập. Lô ${batch.batch_no} đang cách ly — hạn dùng ${formatVnDate(expiryDate)}.`,
      );
      setBatchNo("");
      setNotes("");
      setQuantity("100");
      setMfgDate(todayIso());
      setExpiryDate(plusMonthsIso(12));
    } catch (error) {
      setErr(error instanceof Error ? error.message : "Không thể lưu phiếu nhập kho.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="page-shell stock-in-page">
      <PageHeader
        title="Phiếu nhập kho"
        description="Nhập lô mới vào kho — hệ thống tự đưa vào cách ly và chờ Phòng kiểm nghiệm."
      />

      <ol className="stock-in-steps" aria-label="Quy trình sau khi nhập kho">
        <li className="stock-in-steps__item stock-in-steps__item--current">
          <span className="stock-in-steps__num" aria-hidden="true">
            1
          </span>
          <div>
            <strong>Nhập kho</strong>
            <p className="stock-in-steps__desc">Tạo lô và ghi hạn dùng</p>
          </div>
        </li>
        <li className="stock-in-steps__item">
          <span className="stock-in-steps__num" aria-hidden="true">
            2
          </span>
          <div>
            <strong>Cách ly</strong>
            <p className="stock-in-steps__desc">Chờ lấy mẫu kiểm nghiệm</p>
          </div>
        </li>
        <li className="stock-in-steps__item">
          <span className="stock-in-steps__num" aria-hidden="true">
            3
          </span>
          <div>
            <strong>Kiểm nghiệm</strong>
            <p className="stock-in-steps__desc">Điểm kiểm soát 1</p>
          </div>
        </li>
        <li className="stock-in-steps__item">
          <span className="stock-in-steps__num" aria-hidden="true">
            4
          </span>
          <div>
            <strong>Giải phóng</strong>
            <p className="stock-in-steps__desc">Bộ phận an toàn thực phẩm</p>
          </div>
        </li>
      </ol>
      <p className="stock-in-steps-mobile" aria-hidden="true">
        <span className="stock-in-steps-mobile__track">
          <span className="is-current">1</span>
          <span>2</span>
          <span>3</span>
          <span>4</span>
        </span>
        <span className="stock-in-steps-mobile__copy">
          <strong>Bước 1 / 4 — Nhập kho</strong>
          <span>Tạo lô và ghi hạn dùng</span>
        </span>
      </p>

      {err && (
        <AlertBanner tone="danger" title="Không thể nhập kho" onClose={() => setErr(null)}>
          {err}
        </AlertBanner>
      )}
      {msg && (
        <AlertBanner tone="success" title="Nhập kho thành công" onClose={() => setMsg(null)}>
          {msg}
        </AlertBanner>
      )}

      <div className="stock-in-layout">
        <section className="card form-panel wide stock-in-form">
          <header className="stock-in-form__head">
            <div>
              <h2>Thông tin phiếu nhập</h2>
              <p className="stock-in-form__lead">
                Điền đủ hạn dùng để báo cáo tồn kho hiển thị đúng.
              </p>
            </div>
            <div className="status-list stock-in-form__badges">
              <StatusBadge status="quarantine" />
              <StatusBadge status="pending" label="Chờ kiểm nghiệm" />
            </div>
          </header>

          {selected ? (
            <div className="stock-in-mobile-summary" aria-live="polite">
              <div className="stock-in-mobile-summary__body">
                <ProductThumb src={selected.image_url} label={selected.name} />
                <div>
                  <span className="stock-in-mobile-summary__label">Đang nhập</span>
                  <strong>{selected.name}</strong>
                  <span className="stock-in-mobile-summary__meta">
                    <code>{selected.code}</code>
                    <span>
                      {Number(quantity || 0).toLocaleString("vi-VN")} {selected.unit || "kg"}
                    </span>
                  </span>
                </div>
              </div>
              <StatusBadge status="quarantine" />
            </div>
          ) : null}

          {loading ? (
            <p className="loading-state">Đang tải danh sách vật tư…</p>
          ) : materials.length === 0 ? (
            <p className="loading-state">Chưa có vật tư để nhập kho.</p>
          ) : (
            <form className="form" onSubmit={submit}>
              <div className="form-grid stock-in-form__grid">
                <label className="full">
                  Vật tư cần nhập
                  <select
                    value={materialId}
                    onChange={(event) => setMaterialId(event.target.value)}
                    required
                  >
                    <option value="">— Chọn vật tư —</option>
                    {materials.map((material) => (
                      <option key={material.id} value={material.id}>
                        {material.code} — {material.name}
                        {material.type ? ` (${nhan(LOAI_VAT_TU, material.type)})` : ""}
                      </option>
                    ))}
                  </select>
                </label>

                <label>
                  Số lượng nhập
                  <input
                    value={quantity}
                    onChange={(event) => setQuantity(event.target.value)}
                    type="number"
                    inputMode="decimal"
                    step="0.1"
                    min="0.1"
                    required
                  />
                  <span className="field-hint">Đơn vị: {selected?.unit || "kg"}</span>
                </label>

                <label>
                  Mã lô (tuỳ chọn)
                  <input
                    value={batchNo}
                    onChange={(event) => setBatchNo(event.target.value)}
                    placeholder="Để trống sẽ tự sinh"
                    autoComplete="off"
                  />
                </label>

                <label>
                  Ngày sản xuất
                  <input
                    type="date"
                    value={mfgDate}
                    onChange={(event) => setMfgDate(event.target.value)}
                  />
                </label>

                <label>
                  Hạn dùng
                  <input
                    type="date"
                    value={expiryDate}
                    onChange={(event) => setExpiryDate(event.target.value)}
                    required
                  />
                </label>

                <label className="full">
                  Ghi chú phiếu nhập
                  <textarea
                    value={notes}
                    onChange={(event) => setNotes(event.target.value)}
                    rows={3}
                    placeholder="Ví dụ: giao hàng NCC, số hóa đơn…"
                  />
                </label>

                <div className="full form-actions stock-in-form__actions">
                  <div className="stock-in-form__actions-meta">
                    <span>{selected ? selected.code : "Chưa chọn vật tư"}</span>
                    <strong>
                      {Number(quantity || 0).toLocaleString("vi-VN")} {selected?.unit || "kg"}
                    </strong>
                  </div>
                  <button type="submit" disabled={busy || !materialId}>
                    {busy ? "Đang lưu phiếu…" : "Lưu phiếu nhập kho"}
                  </button>
                </div>
              </div>
            </form>
          )}
        </section>

        <aside className="stock-in-side">
          <section className="card stock-in-preview">
            <h3>Xem trước lô nhập</h3>
            {selected ? (
              <dl className="stock-in-preview__grid">
                <div className="stock-in-preview__product">
                  <dt>Vật tư</dt>
                  <dd className="stock-in-preview__product-dd">
                    <ProductThumb src={selected.image_url} label={selected.name} size="md" />
                    <div>
                      <strong>{selected.name}</strong>
                      <span className="stock-in-preview__meta">
                        <code>{selected.code}</code>
                        {selected.type ? (
                          <span className={`inventory-type inventory-type--${selected.type}`}>
                            {nhan(LOAI_VAT_TU, selected.type)}
                          </span>
                        ) : null}
                      </span>
                    </div>
                  </dd>
                </div>
                <div>
                  <dt>Số lượng</dt>
                  <dd>
                    {Number(quantity || 0).toLocaleString("vi-VN")} {selected.unit || "kg"}
                  </dd>
                </div>
                <div>
                  <dt>Ngày sản xuất</dt>
                  <dd>{formatVnDate(mfgDate)}</dd>
                </div>
                <div>
                  <dt>Hạn dùng</dt>
                  <dd>{formatVnDate(expiryDate)}</dd>
                </div>
                <div className="stock-in-preview__status">
                  <dt>Trạng thái sau nhập</dt>
                  <dd>
                    <div className="status-list">
                      <StatusBadge status="quarantine" />
                    </div>
                  </dd>
                </div>
              </dl>
            ) : (
              <p className="section-description">Chọn vật tư để xem trước thông tin lô.</p>
            )}
          </section>

          <details
            className="card stock-in-tips"
            open={tipsOpen}
            onToggle={(event) => setTipsOpen(event.currentTarget.open)}
          >
            <summary>Lưu ý vận hành</summary>
            <ul>
              <li>Lô mới luôn vào <strong>cách ly</strong>, chưa được xuất hay đưa vào sản xuất.</li>
              <li>Phòng kiểm nghiệm nhập kết quả điểm kiểm soát 1 trước khi gửi phê duyệt.</li>
              <li>Chỉ lô đã giải phóng mới xuất kho hoặc giữ chỗ cho mẻ sản xuất.</li>
            </ul>
          </details>
        </aside>
      </div>
    </div>
  );
}
