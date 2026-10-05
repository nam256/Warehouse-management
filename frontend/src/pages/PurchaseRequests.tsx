import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { createPurchaseRequest, getInventory, getMaterials, getPurchaseRequests } from "../api";
import AlertBanner from "../components/ui/AlertBanner";
import EmptyState from "../components/ui/EmptyState";
import PageHeader from "../components/ui/PageHeader";
import StatusBadge from "../components/ui/StatusBadge";
import { TRANG_THAI_YCMH, nhan } from "../labels";

type PurchaseRow = {
  id: number;
  material_code: string;
  material_name: string;
  requested_qty: number;
  reason?: string | null;
  status: string;
};

type LowStockItem = {
  material_id: number;
  material_code: string;
  material_name: string;
  low_stock: boolean;
};

export default function PurchaseRequests() {
  const [items, setItems] = useState<PurchaseRow[]>([]);
  const [inventory, setInventory] = useState<LowStockItem[]>([]);
  const [materials, setMaterials] = useState<{ id: number; code: string; name: string }[]>([]);
  const [materialId, setMaterialId] = useState("");
  const [qty, setQty] = useState("100");
  const [reason, setReason] = useState("Tồn kho dưới mức tối thiểu");
  const [msg, setMsg] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [formHighlight, setFormHighlight] = useState(false);
  const formRef = useRef<HTMLElement>(null);
  const qtyRef = useRef<HTMLInputElement>(null);

  const reload = useCallback(async () => {
    setErr(null);
    setLoading(true);
    try {
      const [reqs, inv, mats] = await Promise.all([getPurchaseRequests(), getInventory(), getMaterials()]);
      setItems(reqs as PurchaseRow[]);
      setInventory((inv as LowStockItem[]).filter((item) => item.low_stock));
      setMaterials(mats as { id: number; code: string; name: string }[]);
      setMaterialId((current) => {
        if (current) return current;
        const low = (inv as LowStockItem[]).find((item) => item.low_stock);
        if (low) return String(low.material_id);
        return mats[0] ? String(mats[0].id) : "";
      });
    } catch (error) {
      setErr(error instanceof Error ? error.message : "Không thể tải yêu cầu mua hàng.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void reload();
  }, [reload]);

  const selected = useMemo(
    () => materials.find((item) => String(item.id) === materialId) ?? null,
    [materials, materialId],
  );
  const openCount = useMemo(
    () => items.filter((item) => item.status !== "fulfilled" && item.status !== "cancelled").length,
    [items],
  );

  function selectToPurchase(item: LowStockItem) {
    setMaterialId(String(item.material_id));
    setReason(`Tồn kho dưới mức tối thiểu — ${item.material_code}`);
    setMsg(null);
    setErr(null);
    setFormHighlight(true);
    window.requestAnimationFrame(() => {
      formRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      qtyRef.current?.focus();
      qtyRef.current?.select();
    });
    window.setTimeout(() => setFormHighlight(false), 1600);
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setMsg(null);
    setErr(null);
    if (!materialId) {
      setErr("Vui lòng chọn vật tư cần mua.");
      return;
    }
    if (Number(qty) <= 0) {
      setErr("Số lượng yêu cầu phải lớn hơn 0.");
      return;
    }
    setBusy(true);
    try {
      await createPurchaseRequest({
        material_id: Number(materialId),
        requested_qty: Number(qty),
        reason: reason.trim() || "Tồn kho dưới mức tối thiểu",
      });
      await reload();
      setMsg("Đã tạo yêu cầu mua hàng.");
      setQty("100");
    } catch (error) {
      setErr(error instanceof Error ? error.message : "Không thể tạo yêu cầu mua hàng.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="page-shell purchase-page">
      <PageHeader
        title="Yêu cầu mua hàng"
        description="Tạo đề nghị mua khi tồn thấp — theo dõi trạng thái xử lý đến khi hoàn tất."
      />

      <div className="ops-summary">
        <div className={`ops-summary__item${inventory.length > 0 ? " ops-summary__item--warn" : ""}`}>
          <span>Tồn thấp</span>
          <strong>{inventory.length}</strong>
        </div>
        <div className="ops-summary__item">
          <span>Yêu cầu đang mở</span>
          <strong>{openCount}</strong>
        </div>
        <div className="ops-summary__item">
          <span>Tổng yêu cầu</span>
          <strong>{items.length}</strong>
        </div>
      </div>

      {err && (
        <AlertBanner tone="danger" title="Không thể xử lý" onClose={() => setErr(null)}>
          {err}
        </AlertBanner>
      )}
      {msg && (
        <AlertBanner tone="success" title="Thành công" onClose={() => setMsg(null)}>
          {msg}
        </AlertBanner>
      )}

      {inventory.length > 0 && (
        <section className="card purchase-low-stock">
          <h2>Cảnh báo tồn kho thấp</h2>
          <ul className="purchase-low-stock__list">
            {inventory.map((item) => (
              <li key={item.material_id} className="purchase-low-stock__row">
                <strong className="purchase-low-stock__name">{item.material_name}</strong>
                <code className="inventory-code purchase-low-stock__code">{item.material_code}</code>
                <button
                  type="button"
                  className="secondary purchase-low-stock__action"
                  onClick={() => selectToPurchase(item)}
                >
                  Chọn để mua
                </button>
              </li>
            ))}
          </ul>
        </section>
      )}

      <div className="purchase-layout">
        <section
          id="tao-yeu-cau"
          ref={formRef}
          className={`card form-panel wide purchase-form${formHighlight ? " purchase-form--target" : ""}`}
        >
          <header className="ops-form-head">
            <div>
              <h2>Tạo yêu cầu mới</h2>
              <p>Điền số lượng và lý do để bộ phận mua hàng tiếp nhận.</p>
            </div>
          </header>

          {loading && materials.length === 0 ? (
            <p className="loading-state">Đang tải danh sách vật tư…</p>
          ) : materials.length === 0 ? (
            <EmptyState title="Chưa có vật tư" description="Cần có danh mục vật tư trước khi tạo yêu cầu." />
          ) : (
            <form className="form" onSubmit={handleSubmit}>
              <div className="form-grid purchase-form__grid">
                <label className="full">
                  Vật tư cần mua
                  <select value={materialId} onChange={(event) => setMaterialId(event.target.value)} required>
                    <option value="">— Chọn vật tư —</option>
                    {materials.map((material) => (
                      <option key={material.id} value={material.id}>
                        {material.code} — {material.name}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Số lượng yêu cầu
                  <input
                    ref={qtyRef}
                    value={qty}
                    onChange={(event) => setQty(event.target.value)}
                    type="number"
                    inputMode="decimal"
                    step="0.1"
                    min="0.1"
                    required
                  />
                  <span className="field-hint">Đơn vị: kg</span>
                </label>
                <label>
                  Lý do mua hàng
                  <input
                    value={reason}
                    onChange={(event) => setReason(event.target.value)}
                    placeholder="Ví dụ: tồn dưới mức tối thiểu"
                  />
                </label>
                <div className="full form-actions purchase-form__actions">
                  <div className="purchase-form__actions-meta">
                    <span>{selected?.code ?? "Chưa chọn"}</span>
                    <strong>
                      {Number(qty || 0).toLocaleString("vi-VN")} kg
                    </strong>
                  </div>
                  <button type="submit" disabled={busy || !materialId}>
                    {busy ? "Đang tạo…" : "Tạo yêu cầu mua hàng"}
                  </button>
                </div>
              </div>
            </form>
          )}
        </section>

        <aside className="purchase-side">
          <details className="card ops-tips" open>
            <summary>Lưu ý vận hành</summary>
            <ul>
              <li>Ưu tiên tạo yêu cầu cho vật tư đang <strong>tồn thấp</strong>.</li>
              <li>Ghi rõ lý do giúp bộ phận mua hàng phê duyệt nhanh hơn.</li>
              <li>Theo dõi trạng thái đến khi yêu cầu được hoàn tất.</li>
            </ul>
          </details>
        </aside>
      </div>

      <section className="card purchase-list">
        <header className="ops-form-head">
          <div>
            <h2>Danh sách yêu cầu</h2>
            <p>Các đề nghị mua hàng gần đây.</p>
          </div>
        </header>

        {loading && items.length === 0 ? (
          <p className="loading-state">Đang tải yêu cầu…</p>
        ) : items.length === 0 ? (
          <EmptyState title="Chưa có yêu cầu mua hàng" description="Tạo yêu cầu đầu tiên từ form bên trên." />
        ) : (
          <>
            <div className="table-wrap purchase-table">
              <table className="table">
                <thead>
                  <tr>
                    <th>Vật tư</th>
                    <th>Số lượng</th>
                    <th>Lý do</th>
                    <th>Trạng thái</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((row) => (
                    <tr key={row.id}>
                      <td>
                        <strong>{row.material_name}</strong>
                        <div>
                          <code className="inventory-code">{row.material_code}</code>
                        </div>
                      </td>
                      <td>{Number(row.requested_qty).toLocaleString("vi-VN")} kg</td>
                      <td>{row.reason || "—"}</td>
                      <td>
                        <StatusBadge status={row.status} label={nhan(TRANG_THAI_YCMH, row.status)} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <ul className="ops-card-list purchase-cards">
              {items.map((row) => (
                <li key={row.id} className="ops-data-card">
                  <div className="ops-data-card__head">
                    <strong>{row.material_name}</strong>
                    <StatusBadge status={row.status} label={nhan(TRANG_THAI_YCMH, row.status)} />
                  </div>
                  <dl className="ops-data-card__grid">
                    <div>
                      <dt>Mã</dt>
                      <dd>
                        <code className="inventory-code">{row.material_code}</code>
                      </dd>
                    </div>
                    <div>
                      <dt>Số lượng</dt>
                      <dd>{Number(row.requested_qty).toLocaleString("vi-VN")} kg</dd>
                    </div>
                    <div className="full">
                      <dt>Lý do</dt>
                      <dd>{row.reason || "—"}</dd>
                    </div>
                  </dl>
                </li>
              ))}
            </ul>
          </>
        )}
      </section>
    </div>
  );
}
