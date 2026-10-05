import { useEffect, useMemo, useState } from "react";
import {
  downloadBalancePdf,
  downloadInventoryCsv,
  downloadInventoryPdf,
  downloadInventoryPeriodCsv,
  downloadInventoryPeriodPdf,
  downloadIssueLedgerCsv,
  downloadIssueLedgerPdf,
  downloadIssueVoucherPdf,
  downloadLabPdf,
  downloadMixingPdf,
  downloadOperationPdf,
  downloadReceiptPdf,
  getBatches,
  getIssueLedger,
  getLabTests,
  getOrderOperations,
  getProductionOrders,
  type IssueLedgerItem,
} from "../api";
import AlertBanner from "../components/ui/AlertBanner";
import EmptyState from "../components/ui/EmptyState";
import PageHeader from "../components/ui/PageHeader";
import PdfPreviewDialog, { usePdfPreview } from "../components/PdfPreviewDialog";
import { shortRef, sortByRef } from "../shortRef";

function orderedRange(from: string, to: string): { from?: string; to?: string } {
  if (from && to && from > to) return { from: to, to: from };
  return { from: from || undefined, to: to || undefined };
}

function rangeQuery(range: { from?: string; to?: string }): string {
  const query = new URLSearchParams();
  if (range.from) query.set("date_from", range.from);
  if (range.to) query.set("date_to", range.to);
  const suffix = query.toString();
  return suffix ? `?${suffix}` : "";
}

export default function Reports() {
  const [err, setErr] = useState("");
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState("");
  const [batches, setBatches] = useState<{ id: number; batch_no: string }[]>([]);
  const [orders, setOrders] = useState<{ id: number; order_no: string }[]>([]);
  const [tests, setTests] = useState<{ id: number; batch_id: number | null; order_id: number | null }[]>([]);
  const [operations, setOperations] = useState<{ id: number; step: string }[]>([]);
  const [issues, setIssues] = useState<IssueLedgerItem[]>([]);
  const [batchId, setBatchId] = useState("");
  const [orderId, setOrderId] = useState("");
  const [testId, setTestId] = useState("");
  const [operationId, setOperationId] = useState("");
  const [issueId, setIssueId] = useState("");
  const [inventoryView, setInventoryView] = useState<"material" | "batch">("material");
  const [issueFrom, setIssueFrom] = useState("");
  const [issueTo, setIssueTo] = useState("");
  const [periodFrom, setPeriodFrom] = useState("");
  const [periodTo, setPeriodTo] = useState("");
  const pdf = usePdfPreview();

  const selectedBatch = useMemo(
    () => batches.find((b) => b.id === Number(batchId)),
    [batches, batchId],
  );
  const selectedOrder = useMemo(
    () => orders.find((o) => o.id === Number(orderId)),
    [orders, orderId],
  );
  const selectedIssue = useMemo(
    () => issues.find((row) => row.id === Number(issueId)),
    [issues, issueId],
  );
  const testsById = useMemo(() => {
    const batchesById = new Map(batches.map((row) => [row.id, row.batch_no]));
    const ordersById = new Map(orders.map((row) => [row.id, row.order_no]));
    return tests.map((t) => ({
      ...t,
      label: [
        `KQ-${t.id}`,
        t.batch_id && batchesById.get(t.batch_id) ? shortRef(batchesById.get(t.batch_id)) : "",
        t.order_id && ordersById.get(t.order_id) ? shortRef(ordersById.get(t.order_id)) : "",
      ]
        .filter(Boolean)
        .join(" · "),
    }));
  }, [tests, batches, orders]);

  useEffect(() => {
    Promise.all([
      getBatches(),
      getProductionOrders(),
      getLabTests(),
      getIssueLedger().catch(() => [] as IssueLedgerItem[]),
    ])
      .then(([b, o, t, px]) => {
        const batchesSorted = sortByRef(b, (row) => row.batch_no, (row) => row.id);
        const ordersSorted = sortByRef(o, (row) => row.order_no, (row) => row.id);
        const issuesSorted = sortByRef(px, (row) => row.reference_no, (row) => row.id);
        const testsSorted = [...t].sort((a, b) => a.id - b.id);
        setBatches(batchesSorted);
        setOrders(ordersSorted);
        setTests(testsSorted);
        setIssues(issuesSorted);
        if (batchesSorted[0]) setBatchId(String(batchesSorted[0].id));
        if (ordersSorted[0]) setOrderId(String(ordersSorted[0].id));
        if (testsSorted[0]) setTestId(String(testsSorted[0].id));
        if (issuesSorted[0]) setIssueId(String(issuesSorted[0].id));
      })
      .catch(console.error);
  }, []);

  useEffect(() => {
    if (!orderId) {
      setOperations([]);
      setOperationId("");
      return;
    }
    getOrderOperations(Number(orderId))
      .then((ops) => {
        const sorted = [...ops].sort((a, b) => a.id - b.id);
        setOperations(sorted);
        if (sorted[0]) setOperationId(String(sorted[0].id));
        else setOperationId("");
      })
      .catch(() => setOperations([]));
  }, [orderId]);

  async function run(label: string, fn: () => Promise<void>) {
    setErr("");
    setMsg("");
    setLoading(label);
    try {
      await fn();
      setMsg(`Đã tải file: ${label}`);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Lỗi tải file");
    } finally {
      setLoading("");
    }
  }

  async function preview(label: string, path: string, filename: string) {
    setErr("");
    setMsg("");
    setLoading(`Xem ${label}`);
    try {
      await pdf.show(label, path, filename);
      setMsg(`Đang xem trước: ${label}`);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Không thể xem trước phiếu");
    } finally {
      setLoading("");
    }
  }

  const issueRange = orderedRange(issueFrom, issueTo);
  const periodRange = orderedRange(periodFrom, periodTo);
  const batchLabel = selectedBatch ? shortRef(selectedBatch.batch_no) : "Chưa chọn";
  const orderLabel = selectedOrder ? shortRef(selectedOrder.order_no) : "Chưa chọn";
  const issueLabel = selectedIssue ? shortRef(selectedIssue.reference_no) : "";

  return (
    <div className="page-shell reports-page">
      <PageHeader
        title="Báo cáo và xuất biểu mẫu"
        description="Tải nhanh báo cáo kho, hồ sơ sản xuất và kết quả kiểm nghiệm theo biểu mẫu GMP."
      />
      <p className="section-description reports-note">
        Biểu mẫu tuân theo hệ thống quản lý chất lượng GMP — chọn đúng lô hoặc mẻ, bấm <strong>Xem trước</strong> rồi tải xuống.
      </p>

      <div className="ops-summary">
        <div className="ops-summary__item">
          <span>Số báo cáo</span>
          <strong>9</strong>
        </div>
        <div className="ops-summary__item">
          <span>Lô đã chọn</span>
          <strong>{batchLabel}</strong>
        </div>
        <div className="ops-summary__item">
          <span>Mẻ đã chọn</span>
          <strong>{orderLabel}</strong>
        </div>
      </div>

      {err && (
        <AlertBanner tone="danger" title="Không thể tải báo cáo" onClose={() => setErr("")}>
          {err}
        </AlertBanner>
      )}
      {msg && (
        <AlertBanner tone="success" title="Tải báo cáo thành công" onClose={() => setMsg("")}>
          {msg}
        </AlertBanner>
      )}

      <div className="report-grid">
        <section className="card report-section">
          <h3>Báo cáo tồn kho hiện tại</h3>
          <p>
            In tồn vật lý, giữ chỗ và khả dụng cùng một công thức với màn Tồn kho. Chọn theo vật tư
            hoặc theo lô khi hội đồng hỏi Hold-Release / hạn dùng sớm.
          </p>
          <div className="report-actions">
            <label>
              Kiểu xem
              <select
                value={inventoryView}
                onChange={(e) => setInventoryView(e.target.value as "material" | "batch")}
              >
                <option value="material">Theo vật tư</option>
                <option value="batch">Theo lô</option>
              </select>
            </label>
            <button
              type="button"
              disabled={!!loading}
              onClick={() => run("Báo cáo tồn kho (CSV)", () => downloadInventoryCsv(inventoryView))}
            >
              {loading === "Báo cáo tồn kho (CSV)" ? "Đang tải..." : "Tải tệp CSV"}
            </button>
            <button
              type="button"
              className="secondary"
              disabled={!!loading}
              onClick={() =>
                preview(
                  "Báo cáo tồn kho (PDF)",
                  `/reports/inventory/export/pdf?view=${inventoryView}`,
                  "ton-kho.pdf",
                )
              }
            >
              {loading === "Xem Báo cáo tồn kho (PDF)" ? "Đang mở..." : "Xem trước"}
            </button>
            <button
              type="button"
              className="secondary"
              disabled={!!loading}
              onClick={() => run("Báo cáo tồn kho (PDF)", () => downloadInventoryPdf(inventoryView))}
            >
              {loading === "Báo cáo tồn kho (PDF)" ? "Đang tải..." : "Tải tệp PDF"}
            </button>
          </div>
        </section>

        <section className="card report-section">
          <h3>Báo cáo tồn kho theo kỳ</h3>
          <p>
            Tồn đầu / nhập / xuất / hoàn tồn / tồn cuối. Để trống ngày thì lấy từ đầu tháng đến hôm nay.
            Số tính ngược từ sổ movement, không phải khóa sổ kế toán.
          </p>
          <div className="report-actions">
            <label>
              Từ ngày
              <input type="date" value={periodFrom} onChange={(e) => setPeriodFrom(e.target.value)} />
            </label>
            <label>
              Đến ngày
              <input type="date" value={periodTo} onChange={(e) => setPeriodTo(e.target.value)} />
            </label>
            <button
              type="button"
              disabled={!!loading}
              onClick={() => run("Tồn kho theo kỳ (CSV)", () => downloadInventoryPeriodCsv(periodRange))}
            >
              {loading === "Tồn kho theo kỳ (CSV)" ? "Đang tải..." : "Tải tệp CSV"}
            </button>
            <button
              type="button"
              className="secondary"
              disabled={!!loading}
              onClick={() => {
                void preview(
                  "Tồn kho theo kỳ (PDF)",
                  `/reports/inventory/period/export/pdf${rangeQuery(periodRange)}`,
                  "ton-kho-ky.pdf",
                );
              }}
            >
              {loading === "Xem Tồn kho theo kỳ (PDF)" ? "Đang mở..." : "Xem trước"}
            </button>
            <button
              type="button"
              className="secondary"
              disabled={!!loading}
              onClick={() => run("Tồn kho theo kỳ (PDF)", () => downloadInventoryPeriodPdf(periodRange))}
            >
              {loading === "Tồn kho theo kỳ (PDF)" ? "Đang tải..." : "Tải tệp PDF"}
            </button>
          </div>
        </section>

        <section className="card report-section">
          <h3>Sổ xuất kho</h3>
          <p>Danh sách phiếu PX trong kỳ. Để trống ngày thì in toàn bộ phiếu xuất hiện có.</p>
          <div className="report-actions">
            <label>
              Từ ngày
              <input type="date" value={issueFrom} onChange={(e) => setIssueFrom(e.target.value)} />
            </label>
            <label>
              Đến ngày
              <input type="date" value={issueTo} onChange={(e) => setIssueTo(e.target.value)} />
            </label>
            <button
              type="button"
              disabled={!!loading}
              onClick={() => run("Sổ xuất kho (CSV)", () => downloadIssueLedgerCsv(issueRange))}
            >
              {loading === "Sổ xuất kho (CSV)" ? "Đang tải..." : "Tải tệp CSV"}
            </button>
            <button
              type="button"
              className="secondary"
              disabled={!!loading}
              onClick={() => {
                void preview(
                  "Sổ xuất kho (PDF)",
                  `/reports/issues/export/pdf${rangeQuery(issueRange)}`,
                  "so-xuat-kho.pdf",
                );
              }}
            >
              {loading === "Xem Sổ xuất kho (PDF)" ? "Đang mở..." : "Xem trước"}
            </button>
            <button
              type="button"
              className="secondary"
              disabled={!!loading}
              onClick={() => run("Sổ xuất kho (PDF)", () => downloadIssueLedgerPdf(issueRange))}
            >
              {loading === "Sổ xuất kho (PDF)" ? "Đang tải..." : "Tải tệp PDF"}
            </button>
          </div>
        </section>

        <section className="card report-section">
          <h3>Phiếu xuất kho</h3>
          <p>In lại một phiếu PX đã lưu. Biểu mẫu số hóa nội bộ, không thay phiếu giấy pháp lý.</p>
          {issues.length === 0 ? (
            <EmptyState title="Chưa có phiếu xuất trong kỳ" description="Lập phiếu trên trang Xuất kho rồi quay lại đây để in." />
          ) : (
            <div className="report-actions">
              <label>
                Chọn số phiếu
                <select value={issueId} onChange={(e) => setIssueId(e.target.value)}>
                  {issues.map((row) => (
                    <option key={row.id} value={row.id}>
                      {shortRef(row.reference_no)} · {shortRef(row.batch_no)} · {row.quantity} kg
                    </option>
                  ))}
                </select>
              </label>
              <button
                type="button"
                className="secondary"
                disabled={!selectedIssue || !!loading}
                onClick={() =>
                  preview(
                    `Phiếu xuất ${issueLabel}`,
                    `/reports/issues/${selectedIssue!.id}/pdf`,
                    `${issueLabel}.pdf`,
                  )
                }
              >
                {loading === `Xem Phiếu xuất ${issueLabel}` ? "Đang mở..." : "Xem trước"}
              </button>
              <button
                type="button"
                disabled={!selectedIssue || !!loading}
                onClick={() =>
                  run("Phiếu xuất kho", () =>
                    downloadIssueVoucherPdf(selectedIssue!.id, issueLabel),
                  )
                }
              >
                {loading === "Phiếu xuất kho" ? "Đang tải..." : "Tải phiếu PDF"}
              </button>
            </div>
          )}
        </section>

        <section className="card report-section">
          <h3>Phiếu nhập nguyên liệu</h3>
          <p>Xuất phiếu nhập theo SL lúc nhập (không lấy tồn hiện tại nếu lô đã xuất bớt).</p>
          <div className="report-actions">
            <label>
              Chọn lô hàng
              <select value={batchId} onChange={(e) => setBatchId(e.target.value)}>
                {batches.length === 0 && <option value="">Chưa có lô hàng</option>}
                {batches.map((b) => (
                  <option key={b.id} value={b.id}>
                    {shortRef(b.batch_no)}
                  </option>
                ))}
              </select>
            </label>
            <button
              type="button"
              className="secondary"
              disabled={!selectedBatch || !!loading}
              onClick={() =>
                preview(
                  `Phiếu nhập ${batchLabel}`,
                  `/reports/receipt/${selectedBatch!.id}/pdf`,
                  `phieu-nhap-${batchLabel}.pdf`,
                )
              }
            >
              {loading === `Xem Phiếu nhập ${batchLabel}` ? "Đang mở..." : "Xem trước"}
            </button>
            <button
              type="button"
              disabled={!selectedBatch || !!loading}
              onClick={() =>
                run("Phiếu nhập kho", () => downloadReceiptPdf(selectedBatch!.id, batchLabel))
              }
            >
              {loading === "Phiếu nhập kho" ? "Đang tải..." : "Tải phiếu PDF"}
            </button>
          </div>
        </section>

        <section className="card report-section">
          <h3>Biên bản vận hành chưng cất</h3>
          <p>Xuất biên bản ghi nhận nhiệt độ và hàm lượng theo mẻ sản xuất.</p>
          <div className="report-actions">
            <label>
              Chọn mẻ sản xuất
              <select value={orderId} onChange={(e) => setOrderId(e.target.value)}>
                {orders.length === 0 && <option value="">Chưa có mẻ sản xuất</option>}
                {orders.map((o) => (
                  <option key={o.id} value={o.id}>
                    {shortRef(o.order_no)}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Chọn lần ghi nhận
              <select value={operationId} onChange={(e) => setOperationId(e.target.value)}>
                {operations.length === 0 && <option value="">Chưa có dữ liệu vận hành</option>}
                {operations.map((op) => (
                  <option key={op.id} value={op.id}>
                    Lần {op.id} — {op.step}
                  </option>
                ))}
              </select>
            </label>
            <button
              type="button"
              className="secondary"
              disabled={!operationId || !!loading}
              onClick={() =>
                preview(
                  "Thông số vận hành",
                  `/reports/operation/${operationId}/pdf`,
                  `thong-so-van-hanh-${operationId}.pdf`,
                )
              }
            >
              {loading === "Xem Thông số vận hành" ? "Đang mở..." : "Xem trước"}
            </button>
            <button
              type="button"
              disabled={!operationId || !!loading}
              onClick={() => run("Thông số vận hành", () => downloadOperationPdf(Number(operationId)))}
            >
              {loading === "Thông số vận hành" ? "Đang tải..." : "Tải biểu mẫu PDF"}
            </button>
          </div>
        </section>

        <section className="card report-section">
          <h3>Bảng cân đối nguyên liệu</h3>
          <p>Báo cáo đối chiếu nguyên liệu đầu vào và thành phẩm đầu ra của một mẻ.</p>
          <div className="report-actions">
            <label>
              Chọn mẻ sản xuất
              <select value={orderId} onChange={(e) => setOrderId(e.target.value)}>
                {orders.map((o) => (
                  <option key={o.id} value={o.id}>
                    {shortRef(o.order_no)}
                  </option>
                ))}
              </select>
            </label>
            <button
              type="button"
              className="secondary"
              disabled={!selectedOrder || !!loading}
              onClick={() =>
                preview(
                  "Cân bằng nguyên liệu",
                  `/reports/balance/${selectedOrder!.id}/pdf`,
                  `can-bang-nguyen-lieu-${orderLabel}.pdf`,
                )
              }
            >
              {loading === "Xem Cân bằng nguyên liệu" ? "Đang mở..." : "Xem trước"}
            </button>
            <button
              type="button"
              disabled={!selectedOrder || !!loading}
              onClick={() =>
                run("Cân bằng nguyên liệu", () => downloadBalancePdf(selectedOrder!.id, orderLabel))
              }
            >
              {loading === "Cân bằng nguyên liệu" ? "Đang tải..." : "Tải biểu mẫu PDF"}
            </button>
          </div>
        </section>

        <section className="card report-section">
          <h3>Biên bản pha trộn</h3>
          <p>Biểu mẫu ghi nhận công thức và khối lượng pha trộn theo mẻ sản xuất.</p>
          <div className="report-actions">
            <label>
              Chọn mẻ sản xuất
              <select value={orderId} onChange={(e) => setOrderId(e.target.value)}>
                {orders.map((o) => (
                  <option key={o.id} value={o.id}>
                    {shortRef(o.order_no)}
                  </option>
                ))}
              </select>
            </label>
            <button
              type="button"
              className="secondary"
              disabled={!selectedOrder || !!loading}
              onClick={() =>
                preview(
                  "Phiếu pha trộn",
                  `/reports/mixing/${selectedOrder!.id}/pdf`,
                  `phieu-pha-tron-${orderLabel}.pdf`,
                )
              }
            >
              {loading === "Xem Phiếu pha trộn" ? "Đang mở..." : "Xem trước"}
            </button>
            <button
              type="button"
              disabled={!selectedOrder || !!loading}
              onClick={() =>
                run("Phiếu pha trộn", () => downloadMixingPdf(selectedOrder!.id, orderLabel))
              }
            >
              {loading === "Phiếu pha trộn" ? "Đang tải..." : "Tải biểu mẫu PDF"}
            </button>
          </div>
        </section>

        <section className="card report-section">
          <h3>Kết quả sắc ký khí</h3>
          <p>Xuất biên bản kết quả kiểm nghiệm phòng lab.</p>
          <div className="report-actions">
            <label>
              Chọn kết quả kiểm nghiệm
              <select value={testId} onChange={(e) => setTestId(e.target.value)}>
                {testsById.length === 0 && <option value="">Chưa có kết quả kiểm nghiệm</option>}
                {testsById.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.label}
                  </option>
                ))}
              </select>
            </label>
            <button
              type="button"
              className="secondary"
              disabled={!testId || !!loading}
              onClick={() =>
                preview(
                  "Kết quả kiểm nghiệm",
                  `/reports/lab/${testId}/pdf`,
                  `ket-qua-kiem-nghiem-${testId}.pdf`,
                )
              }
            >
              {loading === "Xem Kết quả kiểm nghiệm" ? "Đang mở..." : "Xem trước"}
            </button>
            <button
              type="button"
              disabled={!testId || !!loading}
              onClick={() => run("Kết quả kiểm nghiệm", () => downloadLabPdf(Number(testId)))}
            >
              {loading === "Kết quả kiểm nghiệm" ? "Đang tải..." : "Tải biểu mẫu PDF"}
            </button>
          </div>
        </section>
      </div>
      <PdfPreviewDialog preview={pdf.preview} onClose={pdf.close} onDownload={pdf.download} />
    </div>
  );
}
