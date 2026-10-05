import { useCallback, useEffect, useMemo, useState } from "react";
import {
  createIssue,
  downloadIssueVoucherPdf,
  getBatches,
  getIssueLedger,
  getMaterials,
  getMovements,
  suggestFefo,
  type FefoAllocation,
  type IssueLedgerItem,
  type Material,
  type QualityBatch,
  type User,
} from "../api";
import ProductThumb from "../components/ProductThumb";
import AlertBanner from "../components/ui/AlertBanner";
import EmptyState from "../components/ui/EmptyState";
import PageHeader from "../components/ui/PageHeader";
import PdfPreviewDialog, { usePdfPreview } from "../components/PdfPreviewDialog";
import StatusBadge from "../components/ui/StatusBadge";
import { canWrite, roleHint } from "../roles";
import { shortRef, sortByRef } from "../shortRef";

type Props = { user: User };

function isEligible(batch: QualityBatch) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return (
    batch.available_qty > 0 &&
    batch.quality_status === "released" &&
    batch.ccp1_status === "pass" &&
    (!batch.expiry_date || new Date(batch.expiry_date) >= today)
  );
}

function formatVnDate(value?: string | null): string {
  if (!value) return "—";
  return new Date(`${value}T00:00:00`).toLocaleDateString("vi-VN");
}

export default function StockOut({ user }: Props) {
  const [batches, setBatches] = useState<QualityBatch[]>([]);
  const [materials, setMaterials] = useState<Material[]>([]);
  const [batchId, setBatchId] = useState("");
  const [quantity, setQuantity] = useState("");
  const [issuedQty, setIssuedQty] = useState(0);
  const [msg, setMsg] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [suggestions, setSuggestions] = useState<FefoAllocation[]>([]);
  const [lastIssue, setLastIssue] = useState<{ id: number; reference_no: string } | null>(null);
  const [recentIssues, setRecentIssues] = useState<IssueLedgerItem[]>([]);
  const pdf = usePdfPreview();
  const allowed = canWrite(user, "stock-out");

  const loadBatches = useCallback(async () => {
    setErr(null);
    setLoading(true);
    try {
      const [result, mats, movements, ledger] = await Promise.all([
        getBatches(),
        getMaterials(),
        getMovements(),
        getIssueLedger().catch(() => [] as IssueLedgerItem[]),
      ]);
      const sortedBatches = sortByRef(result, (row) => row.batch_no, (row) => row.id);
      setBatches(sortedBatches);
      setMaterials(mats as Material[]);
      setRecentIssues(ledger.slice(0, 10));
      const outTotal = (movements as { movement_type?: string; quantity?: number }[])
        .filter((row) => row.movement_type === "OUT")
        .reduce((sum, row) => sum + Number(row.quantity || 0), 0);
      setIssuedQty(outTotal);
      const firstEligible = sortedBatches.find(isEligible);
      setBatchId(firstEligible ? String(firstEligible.id) : "");
    } catch (error) {
      const networkError =
        error instanceof TypeError || (error instanceof Error && error.message.includes("Failed to fetch"));
      setErr(
        networkError
          ? "Không kết nối được máy chủ. Kiểm tra backend đang chạy."
          : error instanceof Error
            ? error.message
            : "Không thể tải danh sách lô.",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadBatches();
  }, [loadBatches]);

  const eligible = useMemo(() => batches.filter(isEligible), [batches]);
  const selected = useMemo(
    () => batches.find((batch) => batch.id === Number(batchId)) ?? null,
    [batches, batchId],
  );
  const selectedMaterial = useMemo(
    () => (selected ? materials.find((item) => item.id === selected.material_id) ?? null : null),
    [materials, selected],
  );
  const heldCount = useMemo(
    () => batches.filter((batch) => batch.quantity > 0 && batch.quality_status !== "released").length,
    [batches],
  );

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setMsg(null);
    setErr(null);
    const batch = batches.find((item) => item.id === Number(batchId));
    const qty = Number(quantity);
    if (!batch) {
      setErr("Vui lòng chọn lô hàng hợp lệ.");
      return;
    }
    if (qty <= 0) {
      setErr("Số lượng phải lớn hơn 0.");
      return;
    }
    if (qty > batch.available_qty) {
      setErr(`Tồn khả dụng của lô chỉ còn ${batch.available_qty} kilogram.`);
      return;
    }
    if (!isEligible(batch)) {
      setErr("Lô phải được Bộ phận an toàn thực phẩm giải phóng, đạt điểm kiểm soát 1 và còn hạn trước khi xuất.");
      return;
    }
    setBusy(true);
    try {
      const movement = await createIssue({ batch_id: batch.id, quantity: qty });
      setLastIssue({ id: movement.id, reference_no: movement.reference_no });
      setMsg(`Xuất kho thành công. Số phiếu: ${shortRef(movement.reference_no)}`);
      setSuggestions([]);
      setQuantity("");
      await loadBatches();
    } catch (error) {
      setErr(error instanceof Error ? error.message : "Không thể lập phiếu xuất kho.");
    } finally {
      setBusy(false);
    }
  }

  async function handleSuggest() {
    setErr(null);
    setMsg(null);
    setSuggestions([]);
    const qty = Number(quantity);
    const currentBatch = batches.find((item) => item.id === Number(batchId)) ?? eligible[0];
    if (!currentBatch || qty <= 0) {
      setErr("Chọn lô tham chiếu và nhập số lượng hợp lệ trước khi gợi ý hạn dùng sớm nhất.");
      return;
    }
    setBusy(true);
    try {
      const result = await suggestFefo(currentBatch.material_id, qty);
      if (result.length === 0) {
        setErr("Không có lô đủ điều kiện theo hạn dùng sớm nhất cho số lượng yêu cầu.");
        return;
      }
      setSuggestions(result);
      setBatchId(String(result[0].batch_id));
      setMsg(`Đã gợi ý ${result.length} lô theo hạn dùng gần nhất.`);
    } catch (error) {
      setErr(error instanceof Error ? error.message : "Không thể lấy gợi ý hạn dùng sớm nhất.");
    } finally {
      setBusy(false);
    }
  }

  if (!allowed) {
    return (
      <div className="page-shell stock-out-page">
        <PageHeader title="Phiếu xuất kho" />
        <AlertBanner tone="warning">{roleHint("stock-out")}</AlertBanner>
      </div>
    );
  }

  return (
    <div className="page-shell stock-out-page">
      <PageHeader
        title="Phiếu xuất kho"
        description="Chỉ lô đã giải phóng, đạt điểm kiểm soát 1 và còn hạn mới được xuất."
      />

      <ol className="ops-steps" aria-label="Quy trình xuất kho">
        <li className="ops-steps__item ops-steps__item--current">
          <span className="ops-steps__num">1</span>
          <div>
            <strong>Chọn lô</strong>
            <p>Đã giải phóng & còn hạn</p>
          </div>
        </li>
        <li className="ops-steps__item">
          <span className="ops-steps__num">2</span>
          <div>
            <strong>Phân bổ</strong>
            <p>Ưu tiên hạn dùng sớm</p>
          </div>
        </li>
        <li className="ops-steps__item">
          <span className="ops-steps__num">3</span>
          <div>
            <strong>Xuất kho</strong>
            <p>Ghi nhận phiếu xuất</p>
          </div>
        </li>
      </ol>

      <div className="ops-summary">
        <div className="ops-summary__item">
          <span>Lô đủ điều kiện</span>
          <strong>{eligible.length}</strong>
        </div>
        <div className={`ops-summary__item${heldCount > 0 ? " ops-summary__item--warn" : ""}`}>
          <span>Lô đang giữ</span>
          <strong>{heldCount}</strong>
        </div>
        <div className="ops-summary__item">
          <span>Đã xuất</span>
          <strong>
            {issuedQty.toLocaleString("vi-VN")} <small>kg</small>
          </strong>
        </div>
      </div>

      {err && (
        <AlertBanner tone="danger" title="Không thể xuất kho" onClose={() => setErr(null)}>
          {err}
        </AlertBanner>
      )}
      {msg && (
        <AlertBanner tone="success" title="Thành công" onClose={() => setMsg(null)}>
          {msg}
          {lastIssue ? (
            <div className="report-actions" style={{ marginTop: "0.75rem" }}>
              <button
                type="button"
                className="secondary"
                disabled={busy}
                onClick={() =>
                  void pdf
                    .show(
                      `Phiếu xuất ${shortRef(lastIssue.reference_no)}`,
                      `/reports/issues/${lastIssue.id}/pdf`,
                      `${shortRef(lastIssue.reference_no)}.pdf`,
                    )
                    .catch((error) =>
                      setErr(error instanceof Error ? error.message : "Không thể xem trước phiếu xuất."),
                    )
                }
              >
                Xem trước {shortRef(lastIssue.reference_no)}
              </button>
              <button
                type="button"
                className="secondary"
                disabled={busy}
                onClick={() => void downloadIssueVoucherPdf(lastIssue.id, shortRef(lastIssue.reference_no))}
              >
                Tải phiếu {shortRef(lastIssue.reference_no)}
              </button>
            </div>
          ) : null}
        </AlertBanner>
      )}
      {heldCount > 0 && (
        <AlertBanner tone="warning" title="Có lô đang bị giữ chất lượng">
          Có {heldCount} lô chưa giải phóng — hiển thị trong danh sách nhưng không thể chọn để xuất.
        </AlertBanner>
      )}

      {loading && <p className="loading-state">Đang tải danh sách lô…</p>}
      {!loading && eligible.length === 0 && (
        <EmptyState
          title="Chưa có lô đủ điều kiện xuất"
          description="Chờ Phòng kiểm nghiệm hoàn tất kiểm nghiệm và Bộ phận an toàn thực phẩm phê duyệt chất lượng lô."
        />
      )}

      {!loading && eligible.length > 0 && (
        <div className="stock-out-layout">
          <section className="card form-panel wide stock-out-form">
            <header className="ops-form-head">
              <div>
                <h2>Thông tin phiếu xuất</h2>
                <p>Chọn lô đã giải phóng hoặc dùng gợi ý hạn dùng sớm nhất.</p>
              </div>
            </header>

            <form className="form" onSubmit={submit}>
              <div className="form-grid stock-out-form__grid">
                <label className="full">
                  Lô hàng
                  <select value={batchId} onChange={(event) => setBatchId(event.target.value)} required>
                    {batches
                      .filter((batch) => batch.quantity > 0)
                      .map((batch) => (
                        <option key={batch.id} value={batch.id} disabled={!isEligible(batch)}>
                          {shortRef(batch.batch_no)} — khả dụng {batch.available_qty} kg
                          {!isEligible(batch) ? " (không đủ điều kiện)" : ""}
                        </option>
                      ))}
                  </select>
                </label>

                <label>
                  Số lượng xuất
                  <input
                    value={quantity}
                    onChange={(event) => setQuantity(event.target.value)}
                    type="number"
                    inputMode="decimal"
                    step="0.1"
                    min="0.1"
                    placeholder="Nhập số kg cần xuất"
                    required
                  />
                  <span className="field-hint">Chưa lưu phiếu thì chưa tính đã xuất. Đơn vị: kg</span>
                </label>

                <div className="full form-actions stock-out-form__actions">
                  <div className="stock-out-form__actions-meta">
                    <span>{selected ? shortRef(selected.batch_no) : "Chưa chọn lô"}</span>
                    <strong>
                      {quantity ? `${Number(quantity).toLocaleString("vi-VN")} kg (nháp)` : "Chưa nhập SL"}
                    </strong>
                  </div>
                  <div className="stock-out-form__buttons">
                    <button type="button" className="secondary" onClick={() => void handleSuggest()} disabled={busy}>
                      Gợi ý hạn dùng sớm
                    </button>
                    <button type="submit" disabled={busy || !batchId}>
                      {busy ? "Đang xử lý…" : "Lưu phiếu xuất kho"}
                    </button>
                  </div>
                </div>
              </div>
            </form>

            {suggestions.length > 0 && (
              <div className="stock-out-fefo">
                <h3>Phân bổ đề xuất</h3>
                <ul className="ops-card-list">
                  {suggestions.map((item) => (
                    <li key={item.batch_id} className="ops-mini-card">
                      <strong>{shortRef(item.batch_no)}</strong>
                      <span>
                        {item.qty.toLocaleString("vi-VN")} kg · HSD {formatVnDate(item.expiry_date)}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </section>

          <aside className="stock-out-side">
            <section className="card ops-preview">
              <h3>Xem trước lô xuất</h3>
              {selected ? (
                <dl className="ops-preview__grid">
                  <div className="ops-preview__product">
                    <dt>Lô / vật tư</dt>
                    <dd className="ops-preview__product-dd">
                      <ProductThumb
                        src={selectedMaterial?.image_url}
                        label={selectedMaterial?.name || shortRef(selected.batch_no)}
                        size="md"
                      />
                      <div>
                        <strong>{shortRef(selected.batch_no)}</strong>
                        {selectedMaterial ? (
                          <span className="ops-preview__meta">
                            {selectedMaterial.code} · {selectedMaterial.name}
                          </span>
                        ) : null}
                      </div>
                    </dd>
                  </div>
                  <div>
                    <dt>Khả dụng</dt>
                    <dd>{selected.available_qty.toLocaleString("vi-VN")} kg</dd>
                  </div>
                  <div>
                    <dt>Hạn dùng</dt>
                    <dd>{formatVnDate(selected.expiry_date)}</dd>
                  </div>
                  <div>
                    <dt>Trạng thái</dt>
                    <dd>
                      <div className="status-list">
                        <StatusBadge status={selected.quality_status} />
                        <StatusBadge status={selected.ccp1_status} />
                      </div>
                    </dd>
                  </div>
                </dl>
              ) : (
                <p className="section-description">Chọn lô để xem trước điều kiện xuất.</p>
              )}
            </section>

            <details className="card ops-tips">
              <summary>Lưu ý vận hành</summary>
              <ul>
                <li>Chỉ xuất lô đã <strong>giải phóng</strong> và đạt điểm kiểm soát 1.</li>
                <li>Gợi ý hạn dùng sớm giúp ưu tiên lô gần hết hạn trước.</li>
                <li>Mỗi lần lưu là một lô. Sản xuất đã phân bổ FEFO lúc duyệt mẻ.</li>
                <li>Số lượng xuất không được vượt tồn khả dụng của lô.</li>
              </ul>
            </details>
          </aside>
        </div>
      )}

      {!loading && recentIssues.length > 0 && (
        <section className="card table-card" style={{ marginTop: "1.25rem" }}>
          <h3>Phiếu xuất gần đây</h3>
          <p className="section-description">In lại tối đa 10 phiếu mới nhất.</p>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Số phiếu</th>
                  <th>Lô</th>
                  <th>SL (kg)</th>
                  <th>Loại</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {recentIssues.map((row) => (
                  <tr key={row.id}>
                    <td>
                      <code>{shortRef(row.reference_no)}</code>
                    </td>
                    <td>{shortRef(row.batch_no)}</td>
                    <td>{row.quantity.toLocaleString("vi-VN")}</td>
                    <td>{row.issue_kind}</td>
                    <td>
                      <button
                        type="button"
                        className="secondary"
                        onClick={() =>
                          void pdf
                            .show(
                              `Phiếu xuất ${shortRef(row.reference_no)}`,
                              `/reports/issues/${row.id}/pdf`,
                              `${shortRef(row.reference_no)}.pdf`,
                            )
                            .catch((error) =>
                              setErr(error instanceof Error ? error.message : "Không thể xem trước phiếu xuất."),
                            )
                        }
                      >
                        Xem trước
                      </button>
                      <button
                        type="button"
                        className="secondary"
                        onClick={() => void downloadIssueVoucherPdf(row.id, shortRef(row.reference_no))}
                      >
                        Tải PDF
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
      <PdfPreviewDialog preview={pdf.preview} onClose={pdf.close} onDownload={pdf.download} />
    </div>
  );
}
