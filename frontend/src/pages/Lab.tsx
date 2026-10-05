import { useEffect, useState } from "react";
import {
  createLabTest,
  getBatches,
  getLabSpc,
  getLabTests,
  getProductionOrders,
  importGcCsv,
  type SpcResult,
  type User,
} from "../api";
import AlertBanner, { type AlertTone } from "../components/ui/AlertBanner";
import EmptyState from "../components/ui/EmptyState";
import PageHeader from "../components/ui/PageHeader";
import StatusBadge from "../components/ui/StatusBadge";
import { KET_QUA_CCP, LOAI_KIEM_NGHIEM, nhan } from "../labels";
import { canWrite, roleHint } from "../roles";
import { shortRef, sortByRef } from "../shortRef";

type Props = { user: User };
type Notice = { tone: AlertTone; title: string; text: string };

function formatMetric(value: number | null) {
  return value == null ? "—" : value.toFixed(3);
}

function SpcChart({ result }: { result: SpcResult }) {
  if (result.status !== "ok" || result.points.length === 0) return null;
  const values = result.points.map((point) => point.value);
  const controlValues = [result.lcl, result.ucl, result.mean].filter(
    (value): value is number => value != null,
  );
  const min = Math.min(...values, ...controlValues);
  const max = Math.max(...values, ...controlValues);
  const range = max - min || 1;
  const x = (index: number) =>
    42 + (index * 636) / Math.max(1, result.points.length - 1);
  const y = (value: number) => 220 - ((value - min) / range) * 180;
  const line = result.points.map((point, index) => `${x(index)},${y(point.value)}`).join(" ");

  return (
    <svg className="spc-chart" viewBox="0 0 720 260" role="img" aria-labelledby="spc-chart-title">
      <title id="spc-chart-title">Biểu đồ kiểm soát SPC cho {result.analyte}</title>
      {[result.ucl, result.mean, result.lcl].map((value, index) =>
        value == null ? null : (
          <line
            key={`${index}-${value}`}
            x1="42"
            x2="678"
            y1={y(value)}
            y2={y(value)}
            className={index === 1 ? "spc-chart__mean" : "spc-chart__limit"}
          />
        ),
      )}
      <polyline points={line} className="spc-chart__series" />
      {result.points.map((point, index) => (
        <circle
          key={`${point.tested_at}-${index}`}
          cx={x(index)}
          cy={y(point.value)}
          r={point.out_of_control ? 5 : 3.5}
          fill={point.out_of_control ? "var(--color-danger)" : "var(--color-ok)"}
        >
          <title>
            {shortRef(point.batch_no)}: {point.value}%
          </title>
        </circle>
      ))}
      <text x="42" y="247" className="spc-chart__label">Cũ nhất</text>
      <text x="678" y="247" textAnchor="end" className="spc-chart__label">Mới nhất</text>
    </svg>
  );
}

export default function Lab({ user }: Props) {
  const [tab, setTab] = useState<"manual" | "gc">("manual");
  const [tests, setTests] = useState<Record<string, unknown>[]>([]);
  const [batches, setBatches] = useState<{ id: number; batch_no: string }[]>([]);
  const [orders, setOrders] = useState<{ id: number; order_no: string }[]>([]);
  const [batchId, setBatchId] = useState("");
  const [orderId, setOrderId] = useState("");
  const [c14, setC14] = useState("13.5");
  const [tCa, setTCa] = useState("");
  const [gcData, setGcData] = useState("");
  const [notice, setNotice] = useState<Notice | null>(null);
  const [gcFile, setGcFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string[]>([]);
  const [importing, setImporting] = useState(false);
  const [analyte, setAnalyte] = useState<"C14" | "tCA">("C14");
  const [spc, setSpc] = useState<SpcResult | null>(null);
  const [spcLoading, setSpcLoading] = useState(false);
  const allowed = canWrite(user, "lab");
  const canImport = ["lab", "admin"].includes(user.role);

  async function reload() {
    const [t, b, o] = await Promise.all([getLabTests(), getBatches(), getProductionOrders()]);
    setTests([...t].sort((a, b) => a.id - b.id));
    setBatches(sortByRef(b, (row) => row.batch_no, (row) => row.id));
    setOrders(sortByRef(o, (row) => row.order_no, (row) => row.id));
  }

  useEffect(() => {
    reload().catch((error) =>
      setNotice({
        tone: "danger",
        title: "Không thể tải dữ liệu Lab",
        text: error instanceof Error ? error.message : "Vui lòng thử lại.",
      }),
    );
  }, []);

  useEffect(() => {
    if (tab !== "gc") return;
    void loadSpc();
    // Tải lại chuỗi dữ liệu khi người dùng đổi tab hoặc analyte.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tab, analyte]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setNotice(null);
    if (!batchId && !orderId) {
      setNotice({
        tone: "warning",
        title: "Thiếu đối tượng kiểm nghiệm",
        text: "Vui lòng chọn lô hàng hoặc mẻ sản xuất.",
      });
      return;
    }
    try {
      await createLabTest({
        batch_id: batchId ? Number(batchId) : undefined,
        order_id: orderId ? Number(orderId) : undefined,
        test_type: "GC",
        gc_data: gcData || undefined,
        c14: c14 ? Number(c14) : undefined,
        t_ca_percent: tCa ? Number(tCa) : undefined,
      });
      await reload();
      setNotice({
        tone: "success",
        title: "Đã lưu kết quả",
        text: "Kết quả kiểm nghiệm đã được cập nhật.",
      });
    } catch (err) {
      setNotice({
        tone: "danger",
        title: "Không thể lưu kết quả",
        text: err instanceof Error ? err.message : "Có lỗi xảy ra.",
      });
    }
  }

  async function handleFileChange(file: File | null) {
    setGcFile(file);
    setPreview([]);
    setNotice(null);
    if (!file) return;
    try {
      const text = await file.text();
      setPreview(text.split(/\r?\n/).filter(Boolean).slice(0, 6));
    } catch {
      setNotice({
        tone: "danger",
        title: "Không thể đọc tệp",
        text: "Vui lòng chọn lại tệp CSV mã hóa UTF-8.",
      });
    }
  }

  async function handleGcImport(e: React.FormEvent) {
    e.preventDefault();
    setNotice(null);
    if (!gcFile) {
      setNotice({ tone: "warning", title: "Chưa chọn tệp", text: "Vui lòng chọn tệp CSV GC." });
      return;
    }
    setImporting(true);
    try {
      const result = await importGcCsv(gcFile);
      if (result.duplicate) {
        setNotice({
          tone: "info",
          title: "Tệp đã được nhập",
          text: `Không tạo dữ liệu trùng. Tệp gốc có ${result.row_count} dòng.`,
        });
      } else {
        setNotice({
          tone: "success",
          title: "Import GC thành công",
          text: `Đã nhập nguyên tử ${result.imported} kết quả kiểm nghiệm.`,
        });
      }
      await Promise.all([reload(), loadSpc()]);
    } catch (error) {
      setNotice({
        tone: "danger",
        title: "Import thất bại — không có dòng nào được lưu",
        text: error instanceof Error ? error.message : "Tệp CSV không hợp lệ.",
      });
    } finally {
      setImporting(false);
    }
  }

  async function loadSpc() {
    setSpcLoading(true);
    try {
      setSpc(await getLabSpc(analyte, 100));
    } catch (error) {
      setSpc(null);
      setNotice({
        tone: "danger",
        title: "Không thể tải SPC",
        text: error instanceof Error ? error.message : "Vui lòng thử lại.",
      });
    } finally {
      setSpcLoading(false);
    }
  }

  return (
    <div className="page-shell lab-page">
      <PageHeader
        title="Phòng kiểm nghiệm"
        description="Ghi nhận thủ công hoặc import CSV từ GC, đồng thời theo dõi giới hạn kiểm soát SPC."
      />

      <div className="ops-summary">
        <div className="ops-summary__item">
          <span>Số kết quả</span>
          <strong>{tests.length}</strong>
        </div>
        <div className="ops-summary__item">
          <span>Tab hiện tại</span>
          <strong>{tab === "manual" ? "Nhập thủ công" : "Import GC & SPC"}</strong>
        </div>
        {tab === "gc" && (
          <div className="ops-summary__item">
            <span>Chỉ tiêu SPC</span>
            <strong>{analyte}</strong>
          </div>
        )}
      </div>

      <div className="page-tabs" role="tablist" aria-label="Chức năng phòng kiểm nghiệm">
        <button
          type="button"
          role="tab"
          aria-selected={tab === "manual"}
          className={tab === "manual" ? "active" : ""}
          onClick={() => setTab("manual")}
        >
          Nhập thủ công
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={tab === "gc"}
          className={tab === "gc" ? "active" : ""}
          onClick={() => setTab("gc")}
        >
          Import GC & SPC
        </button>
      </div>

      {!allowed && (
        <AlertBanner tone="warning" title="Quyền chỉ xem">
          {roleHint("lab")}
        </AlertBanner>
      )}
      {notice && (
        <AlertBanner tone={notice.tone} title={notice.title} onClose={() => setNotice(null)}>
          {notice.text}
        </AlertBanner>
      )}

      {tab === "manual" && (
        <>
          {allowed && (
            <div className="lab-create">
              <section className="card form-panel wide lab-form">
                <header className="ops-form-head">
                  <div>
                    <h2>Nhập kết quả sắc ký khí</h2>
                    <p>Ghi nhận điểm kiểm soát 1 theo lô hàng hoặc mẻ sản xuất.</p>
                  </div>
                </header>
                <form className="form" onSubmit={handleSubmit}>
                  <div className="form-grid lab-form__grid">
                    <label>
                      Lô hàng
                      <select value={batchId} onChange={(e) => setBatchId(e.target.value)}>
                        <option value="">— Tùy chọn —</option>
                        {batches.map((b) => (
                          <option key={b.id} value={b.id}>
                            {shortRef(b.batch_no)}
                          </option>
                        ))}
                      </select>
                    </label>
                    <label>
                      Mẻ sản xuất
                      <select value={orderId} onChange={(e) => setOrderId(e.target.value)}>
                        <option value="">— Tùy chọn —</option>
                        {orders.map((o) => (
                          <option key={o.id} value={o.id}>
                            {shortRef(o.order_no)}
                          </option>
                        ))}
                      </select>
                    </label>
                    <label>
                      Chỉ số C14 — điểm kiểm soát 1 (dpm/gC)
                      <input value={c14} onChange={(e) => setC14(e.target.value)} type="number" step="0.01" />
                    </label>
                    <label>
                      Hàm lượng thành phần chính (%)
                      <input value={tCa} onChange={(e) => setTCa(e.target.value)} type="number" step="0.01" />
                    </label>
                    <label className="full">
                      Dữ liệu sắc ký khí
                      <textarea value={gcData} onChange={(e) => setGcData(e.target.value)} rows={3} />
                    </label>
                    <div className="full form-actions">
                      <button type="submit">Lưu kết quả</button>
                    </div>
                  </div>
                </form>
              </section>

              <aside className="lab-create__side">
                <section className="card ops-preview">
                  <h3>Điểm kiểm soát 1</h3>
                  <dl className="ops-preview__grid">
                    <div>
                      <dt>Đối tượng</dt>
                      <dd>
                        <strong>
                          {batchId
                            ? shortRef(batches.find((b) => String(b.id) === batchId)?.batch_no) || "Lô đã chọn"
                            : orderId
                              ? shortRef(orders.find((o) => String(o.id) === orderId)?.order_no) || "Mẻ đã chọn"
                              : "Chưa chọn"}
                        </strong>
                      </dd>
                    </div>
                    <div>
                      <dt>Chỉ số C14</dt>
                      <dd>{c14 ? `${c14} dpm/gC` : "—"}</dd>
                    </div>
                    <div>
                      <dt>Thành phần chính</dt>
                      <dd>{tCa ? `${tCa} %` : "—"}</dd>
                    </div>
                  </dl>
                </section>
                <details className="card ops-tips" open>
                  <summary>Lưu ý vận hành</summary>
                  <ul>
                    <li>Chọn <strong>lô hàng</strong> hoặc <strong>mẻ sản xuất</strong> trước khi lưu.</li>
                    <li>Chỉ số C14 dùng cho điểm kiểm soát 1 trên nguyên liệu.</li>
                    <li>Kết quả đạt mới được gửi Bộ phận an toàn thực phẩm phê duyệt.</li>
                  </ul>
                </details>
              </aside>
            </div>
          )}

          <section className="card lab-results">
            <header className="ops-form-head">
              <div>
                <h2>Kết quả kiểm nghiệm</h2>
                <p>Danh sách kết quả kiểm nghiệm thủ công và điểm kiểm soát 1 gần đây.</p>
              </div>
            </header>
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Loại kiểm nghiệm</th>
                    <th>Chỉ số C14</th>
                    <th>Hàm lượng (%)</th>
                    <th>Kết quả</th>
                    <th>Thời gian</th>
                  </tr>
                </thead>
                <tbody>
                  {tests.map((t) => (
                    <tr key={String(t.id)}>
                      <td>{nhan(LOAI_KIEM_NGHIEM, String(t.test_type))}</td>
                      <td>{t.c14 != null ? String(t.c14) : "—"}</td>
                      <td>{t.t_ca_percent != null ? String(t.t_ca_percent) : "—"}</td>
                      <td>
                        <StatusBadge status={String(t.result_status)} label={nhan(KET_QUA_CCP, String(t.result_status))} />
                      </td>
                      <td>{String(t.created_at).slice(0, 19)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <ul className="ops-card-list lab-result-cards">
              {tests.map((t) => (
                <li key={String(t.id)} className="ops-data-card">
                  <div className="ops-data-card__head">
                    <strong>{nhan(LOAI_KIEM_NGHIEM, String(t.test_type))}</strong>
                    <StatusBadge status={String(t.result_status)} label={nhan(KET_QUA_CCP, String(t.result_status))} />
                  </div>
                  <dl className="ops-data-card__grid">
                    <div>
                      <dt>Chỉ số C14</dt>
                      <dd>{t.c14 != null ? String(t.c14) : "—"}</dd>
                    </div>
                    <div>
                      <dt>Hàm lượng (%)</dt>
                      <dd>{t.t_ca_percent != null ? String(t.t_ca_percent) : "—"}</dd>
                    </div>
                    <div>
                      <dt>Thời gian</dt>
                      <dd>{String(t.created_at).slice(0, 19)}</dd>
                    </div>
                  </dl>
                </li>
              ))}
            </ul>
          </section>
        </>
      )}

      {tab === "gc" && (
        <div className="lab-gc-grid">
          <section className="card">
            <h2 className="section-title">Import tệp GC</h2>
            <p className="section-description">
              CSV tối đa 1 MB/1.000 dòng. Cột: batch_no, analyte, value, unit và tested_at tùy chọn.
              Mẫu thử dùng lô <code>NVL-GC-001</code> (đã tạo khi demo).
            </p>
            <p>
              <a href="/samples/gc-import-mau.csv" download="gc-import-mau.csv">
                Tải CSV mẫu thử
              </a>
            </p>
            {canImport ? (
              <form className="form" onSubmit={handleGcImport}>
                <label>
                  Tệp CSV
                  <input
                    type="file"
                    accept=".csv,text/csv,application/vnd.ms-excel"
                    onChange={(event) => void handleFileChange(event.target.files?.[0] ?? null)}
                  />
                </label>
                <button type="submit" disabled={importing}>
                  {importing ? "Đang kiểm tra toàn bộ tệp…" : "Kiểm tra và import"}
                </button>
              </form>
            ) : (
              <AlertBanner tone="info" title="Không có quyền import">
                Chỉ tài khoản Lab hoặc Quản trị viên được nhập CSV; bạn vẫn có thể xem SPC.
              </AlertBanner>
            )}
            {preview.length > 0 && (
              <div className="gc-preview" aria-label="Xem trước tệp CSV">
                <strong>Xem trước {Math.max(0, preview.length - 1)} dòng đầu</strong>
                <pre>{preview.join("\n")}</pre>
              </div>
            )}
          </section>

          <section className="card spc-panel">
            <div className="spc-panel__header">
              <div>
                <h2 className="section-title">Biểu đồ kiểm soát SPC</h2>
                <p className="section-description">Giới hạn kiểm soát = trung bình ± 3σ.</p>
              </div>
              <label>
                Chỉ tiêu
                <select value={analyte} onChange={(event) => setAnalyte(event.target.value as "C14" | "tCA")}>
                  <option value="C14">C14</option>
                  <option value="tCA">tCA</option>
                </select>
              </label>
            </div>
            {spcLoading ? (
              <p>Đang tải dữ liệu SPC…</p>
            ) : !spc || spc.status === "insufficient_data" ? (
              <EmptyState
                title="Chưa đủ dữ liệu SPC"
                description={`Cần ít nhất 10 điểm cùng analyte; hiện có ${spc?.points.length ?? 0} điểm.`}
                action={<button type="button" onClick={() => void loadSpc()}>Tải lại</button>}
              />
            ) : (
              <>
                <div className="spc-metrics">
                  <div><span>Trung bình</span><strong>{formatMetric(spc.mean)}</strong></div>
                  <div><span>Độ lệch chuẩn</span><strong>{formatMetric(spc.std_dev)}</strong></div>
                  <div><span>UCL</span><strong>{formatMetric(spc.ucl)}</strong></div>
                  <div><span>LCL</span><strong>{formatMetric(spc.lcl)}</strong></div>
                </div>
                <SpcChart result={spc} />
                {spc.points.some((point) => point.out_of_control) ? (
                  <AlertBanner tone="danger" title="Có điểm ngoài giới hạn kiểm soát">
                    Phát hiện {spc.points.filter((point) => point.out_of_control).length} điểm cần điều tra.
                  </AlertBanner>
                ) : (
                  <AlertBanner tone="success" title="Quá trình trong giới hạn">
                    Chưa phát hiện điểm ngoài UCL/LCL trong chuỗi đang xem.
                  </AlertBanner>
                )}
              </>
            )}
          </section>
        </div>
      )}
    </div>
  );
}
