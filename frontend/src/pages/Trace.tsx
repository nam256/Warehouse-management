import { useEffect, useState } from "react";
import {
  createRecallSimulation,
  downloadAuthenticated,
  downloadRecallCsv,
  getBatchPassport,
  getBatchQr,
  getTraceSuggestions,
  traceBatch,
  type BatchPassport,
  type BatchTraceSuggest,
  type RecallAffectedBatch,
  type RecallSimulation,
  type User,
} from "../api";
import ActionBar from "../components/ui/ActionBar";
import AlertBanner from "../components/ui/AlertBanner";
import DataTable, { type DataTableColumn } from "../components/ui/DataTable";
import EmptyState from "../components/ui/EmptyState";
import FilterBar from "../components/ui/FilterBar";
import PageHeader from "../components/ui/PageHeader";
import StatusBadge from "../components/ui/StatusBadge";
import { HUONG_TRUY_XUAT, KET_QUA_CCP, LOAI_VAT_TU, TRANG_THAI_ME, nhan } from "../labels";

type TraceData = {
  batch_no: string;
  direction: string;
  input_batches: { batch_no: string; material_code: string; quantity: number; ccp_status?: string }[];
  production_orders: { order_no: string; status: string; planned_qty: number; actual_qty: number | null }[];
  output_batches: { batch_no: string; material_code: string; quantity: number; ccp_status?: string }[];
};

type Props = { user: User };

function displayDate(value: string | null) {
  return value ? new Date(value).toLocaleDateString("vi-VN") : "—";
}

const recallColumns: DataTableColumn<RecallAffectedBatch>[] = [
  { key: "level", header: "Tầng", render: (row) => row.depth },
  { key: "batch", header: "Lô ảnh hưởng", render: (row) => <strong>{row.batch_no}</strong> },
  { key: "material", header: "Vật tư", render: (row) => row.material || "—" },
  { key: "order", header: "Lệnh sản xuất", render: (row) => row.order_no ?? "Lô nguồn" },
  { key: "quantity", header: "Số lượng", render: (row) => `${row.quantity} kg` },
  {
    key: "quality",
    header: "Trạng thái chất lượng",
    render: (row) => <StatusBadge status={row.quality_status} />,
  },
];

export default function Trace({ user }: Props) {
  const [batchNo, setBatchNo] = useState("");
  const [suggestions, setSuggestions] = useState<BatchTraceSuggest[]>([]);
  const [data, setData] = useState<TraceData | null>(null);
  const [passport, setPassport] = useState<BatchPassport | null>(null);
  const [qrUrl, setQrUrl] = useState("");
  const [reason, setReason] = useState("");
  const [recall, setRecall] = useState<RecallSimulation | null>(null);
  const [err, setErr] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const [recallLoading, setRecallLoading] = useState(false);
  const canRecall = ["attp", "ql_nm", "admin"].includes(user.role);

  useEffect(() => {
    getTraceSuggestions()
      .then(setSuggestions)
      .catch((error) => setErr(error instanceof Error ? error.message : "Không thể tải gợi ý mã lô."));
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      getTraceSuggestions(batchNo)
        .then(setSuggestions)
        .catch((error) => setErr(error instanceof Error ? error.message : "Không thể lọc mã lô."));
    }, 250);
    return () => window.clearTimeout(timer);
  }, [batchNo]);

  useEffect(() => () => {
    if (qrUrl) URL.revokeObjectURL(qrUrl);
  }, [qrUrl]);

  useEffect(() => {
    const initialBatch = new URLSearchParams(window.location.search).get("batch");
    if (initialBatch) void runSearch(initialBatch);
    // Chỉ đọc tham số QR khi mở trang lần đầu.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function runSearch(code: string) {
    const trimmed = code.trim();
    if (!trimmed) return;
    setBatchNo(trimmed);
    setErr("");
    setSuccess("");
    setData(null);
    setPassport(null);
    setRecall(null);
    setLoading(true);
    try {
      const [traceResult, passportResult, qrBlob] = await Promise.all([
        traceBatch(trimmed),
        getBatchPassport(trimmed),
        getBatchQr(trimmed),
      ]);
      setData(traceResult);
      setPassport(passportResult);
      setQrUrl(URL.createObjectURL(qrBlob));
      window.history.replaceState(null, "", `/trace?batch=${encodeURIComponent(trimmed)}`);
    } catch (error) {
      setErr(error instanceof Error ? error.message : "Không thể tải hồ sơ lô.");
    } finally {
      setLoading(false);
    }
  }

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    await runSearch(batchNo);
  }

  async function handleRecall(e: React.FormEvent) {
    e.preventDefault();
    if (!passport || !reason.trim()) {
      setErr("Vui lòng nhập lý do mô phỏng thu hồi.");
      return;
    }
    setErr("");
    setSuccess("");
    setRecallLoading(true);
    try {
      const result = await createRecallSimulation(passport.batch_no, reason.trim());
      setRecall(result);
      setSuccess(`Đã mô phỏng ${result.affected_batches.length} lô ảnh hưởng trong ${result.duration_ms} ms.`);
    } catch (error) {
      setErr(error instanceof Error ? error.message : "Không thể chạy mô phỏng thu hồi.");
    } finally {
      setRecallLoading(false);
    }
  }

  async function handleCsvDownload() {
    if (!recall) return;
    setErr("");
    try {
      await downloadRecallCsv(recall.id);
    } catch (error) {
      setErr(error instanceof Error ? error.message : "Không thể tải CSV.");
    }
  }

  async function handleCertificateDownload() {
    if (!passport?.certificate_url) return;
    setErr("");
    try {
      await downloadAuthenticated(
        passport.certificate_url.replace("/api/v1", ""),
        `chung-nhan-giai-phong-${passport.batch_no}.pdf`,
      );
    } catch (error) {
      setErr(error instanceof Error ? error.message : "Không thể tải chứng nhận.");
    }
  }

  return (
    <div className="page-shell trace-page">
      <PageHeader
        title="Hộ chiếu lô & mô phỏng thu hồi"
        description="Truy xuất nguồn gốc, xem QR và xác định toàn bộ lô downstream nhiều tầng."
      />
      <form className="trace-search-form" onSubmit={handleSearch}>
        <FilterBar ariaLabel="Tra cứu hộ chiếu lô">
          <label className="trace-search-field">
            Mã lô hàng
            <input
              value={batchNo}
              onChange={(e) => setBatchNo(e.target.value)}
              list="trace-batch-suggestions"
              placeholder="Gõ hoặc chọn mã lô, ví dụ NVL-20260624-001"
              autoComplete="off"
            />
            <datalist id="trace-batch-suggestions">
              {suggestions.map((s) => (
                <option key={s.batch_no} value={s.batch_no}>
                  {s.material_code} — {s.trace_hint}
                </option>
              ))}
            </datalist>
          </label>
          <button type="submit" className="trace-search-submit" disabled={loading}>
            {loading ? "Đang tra cứu…" : "Tra cứu"}
          </button>
        </FilterBar>
      </form>

      {suggestions.length > 0 && (
        <div className="card">
          <h3 style={{ marginTop: 0, fontSize: "1rem" }}>Gợi ý mã lô — bấm để tra cứu nhanh</h3>
          <p style={{ fontSize: "0.875rem", color: "#64748b", margin: "0 0 0.75rem" }}>
            Liệt kê các lô gần đây (nguyên liệu và thành phẩm). Gõ vào ô trên để lọc theo mã lô hoặc tên vật tư.
          </p>
          <div className="trace-chips">
            {suggestions.map((s) => (
              <button
                key={s.batch_no}
                type="button"
                className={`trace-chip${batchNo === s.batch_no ? " active" : ""}`}
                onClick={() => runSearch(s.batch_no)}
                title={s.trace_hint}
              >
                <strong>{s.batch_no}</strong>
                <span>
                  {s.material_code} · {nhan(LOAI_VAT_TU, s.material_type)}
                  {s.quantity > 0 ? ` · ${s.quantity} kg` : ""}
                </span>
              </button>
            ))}
          </div>
        </div>
      )}

      {err && <AlertBanner tone="danger" title="Không thể hoàn tất" onClose={() => setErr("")}>{err}</AlertBanner>}
      {success && <AlertBanner tone="success" onClose={() => setSuccess("")}>{success}</AlertBanner>}
      {!loading && !data && <EmptyState title="Chưa chọn lô" description="Nhập hoặc chọn một mã lô để xem hộ chiếu số." />}

      {passport && (
        <>
          <div className="ops-summary">
            <div className="ops-summary__item">
              <span>Mã lô</span>
              <strong>{passport.batch_no}</strong>
            </div>
            <div className="ops-summary__item">
              <span>Chất lượng</span>
              <strong>
                <StatusBadge status={passport.quality_status} />
              </strong>
            </div>
            <div className="ops-summary__item">
              <span>Số lượng</span>
              <strong>{passport.quantity.toLocaleString("vi-VN")} kg</strong>
            </div>
          </div>

          <div className="grid trace-passport-grid">
            <section className="card trace-passport">
              <header className="ops-form-head">
                <div>
                  <h2>Hộ chiếu lô {passport.batch_no}</h2>
                  <p>Nguồn gốc, chất lượng và điểm kiểm soát của lô.</p>
                </div>
                <div className="status-list">
                  <StatusBadge status={passport.quality_status} />
                  <StatusBadge status={passport.ccp_status} />
                </div>
              </header>
              <dl className="ops-data-card__grid trace-passport__grid">
                <div className="full">
                  <dt>Vật tư</dt>
                  <dd>
                    <strong>{passport.material_name}</strong> — {passport.material_code}
                  </dd>
                </div>
                <div>
                  <dt>Nhà cung cấp</dt>
                  <dd>{passport.supplier_name ?? "Nội bộ sản xuất"}</dd>
                </div>
                <div>
                  <dt>Ngày nhập/sản xuất</dt>
                  <dd>{displayDate(passport.mfg_date ?? passport.received_at)}</dd>
                </div>
                <div>
                  <dt>Hạn dùng</dt>
                  <dd>{displayDate(passport.expiry_date)}</dd>
                </div>
                <div>
                  <dt>Số lượng</dt>
                  <dd>{passport.quantity.toLocaleString("vi-VN")} kg</dd>
                </div>
                <div className="full">
                  <dt>Lệnh nguồn</dt>
                  <dd>
                    {passport.source_order
                      ? `${passport.source_order.order_no} (${nhan(TRANG_THAI_ME, passport.source_order.status)})`
                      : "Không có"}
                  </dd>
                </div>
              </dl>
              {passport.certificate_url && (
                <ActionBar align="start">
                  <button type="button" className="secondary" onClick={handleCertificateDownload}>
                    Tải chứng nhận giải phóng
                  </button>
                </ActionBar>
              )}
            </section>
            <section className="card trace-qr">
              <header className="ops-form-head">
                <div>
                  <h2>QR hộ chiếu số</h2>
                  <p>Quét mã để mở nhanh hồ sơ truy xuất trên thiết bị di động.</p>
                </div>
              </header>
              {qrUrl && <img src={qrUrl} alt={`QR truy xuất lô ${passport.batch_no}`} width="220" height="220" />}
              <p className="section-description">Quét để mở: /trace?batch={passport.batch_no}</p>
            </section>
          </div>
        </>
      )}

      {data && (
        <div className="grid trace-lineage">
          <section className="card">
            <header className="ops-form-head">
              <div>
                <h3>Lô: {data.batch_no}</h3>
                <p>Loại lô: {nhan(HUONG_TRUY_XUAT, data.direction)}</p>
              </div>
            </header>
            <h4 className="trace-lineage__subhead">Mẻ sản xuất liên quan</h4>
            {data.production_orders.length > 0 ? (
              <ul className="ops-card-list">
                {data.production_orders.map((o) => (
                  <li key={o.order_no} className="ops-mini-card">
                    <strong>{o.order_no}</strong>
                    <span>
                      {nhan(TRANG_THAI_ME, o.status)} · Kế hoạch {o.planned_qty} kg
                      {o.actual_qty != null ? ` · Thực tế ${o.actual_qty} kg` : ""}
                    </span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="section-description">Không có mẻ sản xuất liên quan.</p>
            )}
          </section>
          <section className="card">
            <header className="ops-form-head">
              <div>
                <h4>Nguyên liệu đầu vào</h4>
                <p>Các lô nguyên liệu đã dùng để tạo ra lô này.</p>
              </div>
            </header>
            {data.input_batches.length > 0 ? (
              <ul className="ops-card-list">
                {data.input_batches.map((b) => (
                  <li key={b.batch_no} className="ops-mini-card">
                    <strong>{b.batch_no}</strong>
                    <span>
                      {b.material_code} · {b.quantity} kg · Điểm kiểm soát:{" "}
                      {b.ccp_status ? nhan(KET_QUA_CCP, b.ccp_status) : "—"}
                    </span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="section-description">Không có.</p>
            )}
          </section>
          <section className="card">
            <header className="ops-form-head">
              <div>
                <h4>
                  Thành phẩm đầu ra
                  {data.direction === "TP" && data.output_batches.some((b) => b.batch_no === data.batch_no) && (
                    <span className="trace-lineage__hint"> (lô đang tra cứu)</span>
                  )}
                </h4>
                <p>Lô thành phẩm được tạo ra từ lô này, nếu có.</p>
              </div>
            </header>
            {data.output_batches.length > 0 ? (
              <ul className="ops-card-list">
                {data.output_batches.map((b) => (
                  <li key={b.batch_no} className="ops-mini-card">
                    <strong>{b.batch_no}</strong>
                    <span>
                      {b.material_code} · {b.quantity} kg
                      {b.batch_no === data.batch_no ? " · đầu ra mẻ sản xuất" : ""}
                    </span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="section-description">Không có — lô này chưa được dùng làm NVL cho mẻ SX khác.</p>
            )}
            {data.direction === "NVL" && !data.output_batches.length && (
              <p className="section-description">
                Tra cứu lô thành phẩm (TP-…) sau khi hoàn thành mẻ sản xuất để xem chuỗi đầy đủ.
              </p>
            )}
          </section>
        </div>
      )}

      {passport && canRecall && (
        <section className="card trace-recall">
          <header className="ops-form-head">
            <div>
              <h2>Mô phỏng thu hồi</h2>
              <p>Xác định toàn bộ lô và lệnh sản xuất downstream bị ảnh hưởng nếu thu hồi lô này.</p>
            </div>
          </header>
          <form onSubmit={handleRecall}>
            <FilterBar ariaLabel="Thông tin mô phỏng thu hồi">
              <label>
                Lý do mô phỏng
                <input
                  value={reason}
                  onChange={(event) => setReason(event.target.value)}
                  placeholder="Ví dụ: nghi ngờ nguyên liệu không phù hợp"
                  required
                />
              </label>
              <button type="submit" disabled={recallLoading}>
                {recallLoading ? "Đang duyệt chuỗi…" : "Chạy mô phỏng"}
              </button>
            </FilterBar>
          </form>
          {recall ? (
            <>
              <ActionBar align="between">
                <p>
                  <strong>{recall.affected_batches.length}</strong> lô,{" "}
                  <strong>{recall.affected_orders.length}</strong> lệnh sản xuất — {recall.duration_ms} ms
                </p>
                <button type="button" className="secondary" onClick={handleCsvDownload}>Tải CSV</button>
              </ActionBar>
              <DataTable
                caption="Các lô bị ảnh hưởng trong mô phỏng"
                columns={recallColumns}
                rows={recall.affected_batches}
                rowKey={(row) => row.batch_id}
              />
              <ul className="ops-card-list trace-cards">
                {recall.affected_batches.map((row) => (
                  <li key={row.batch_id} className="ops-data-card">
                    <div className="ops-data-card__head">
                      <strong>{row.batch_no}</strong>
                      <StatusBadge status={row.quality_status} />
                    </div>
                    <dl className="ops-data-card__grid">
                      <div>
                        <dt>Tầng</dt>
                        <dd>{row.depth}</dd>
                      </div>
                      <div>
                        <dt>Vật tư</dt>
                        <dd>{row.material || "—"}</dd>
                      </div>
                      <div>
                        <dt>Lệnh sản xuất</dt>
                        <dd>{row.order_no ?? "Lô nguồn"}</dd>
                      </div>
                      <div>
                        <dt>Số lượng</dt>
                        <dd>{row.quantity} kg</dd>
                      </div>
                    </dl>
                  </li>
                ))}
              </ul>
            </>
          ) : (
            <EmptyState
              title="Chưa có kết quả mô phỏng"
              description="Mô phỏng chỉ đọc, không thay đổi tồn kho hoặc trạng thái chất lượng."
            />
          )}
        </section>
      )}
      {passport && !canRecall && (
        <AlertBanner tone="info">
          Vai trò ATTP, quản lý nhà máy hoặc quản trị viên mới được chạy mô phỏng thu hồi.
        </AlertBanner>
      )}
    </div>
  );
}
