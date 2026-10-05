import { useCallback, useEffect, useMemo, useState } from "react";
import { downloadHaccpPdf, getHaccpMonitor } from "../api";
import AlertBanner from "../components/ui/AlertBanner";
import EmptyState from "../components/ui/EmptyState";
import PageHeader from "../components/ui/PageHeader";
import StatusBadge from "../components/ui/StatusBadge";
import { formatVnDateTime } from "../datetime";
import { KET_QUA_CCP, nhan } from "../labels";

type Ccp1Row = {
  id: string;
  batch_no: string;
  c14: string;
  statusRaw: string;
  status: string;
  at: string;
};

type Ccp2Row = {
  id: string;
  order_no: string;
  step: string;
  t_top: string;
  t_ca_percent: string;
  statusRaw: string;
  status: string;
  at: string;
};

export default function Haccp() {
  const [data, setData] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);
  const [exportErr, setExportErr] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setErr(null);
    try {
      setData(await getHaccpMonitor(14));
    } catch (error) {
      setErr(error instanceof Error ? error.message : "Không thể tải dữ liệu giám sát.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const ccp1 = useMemo<Ccp1Row[]>(() => {
    if (!data) return [];
    return ((data.ccp1_records as Record<string, unknown>[]) || []).map((row, index) => ({
      id: String(row.id ?? `${row.batch_no}-${index}`),
      batch_no: String(row.batch_no ?? "—"),
      c14: String(row.c14 ?? "—"),
      statusRaw: String(row.status ?? ""),
      status: nhan(KET_QUA_CCP, String(row.status)),
      at: formatVnDateTime(String(row.at)),
    }));
  }, [data]);

  const ccp2 = useMemo<Ccp2Row[]>(() => {
    if (!data) return [];
    return ((data.ccp2_records as Record<string, unknown>[]) || []).map((row, index) => ({
      id: String(row.id ?? `${row.order_no}-${index}`),
      order_no: String(row.order_no ?? "—"),
      step: String(row.step ?? "—"),
      t_top: String(row.t_top ?? "—"),
      t_ca_percent: String(row.t_ca_percent ?? "—"),
      statusRaw: String(row.status ?? ""),
      status: nhan(KET_QUA_CCP, String(row.status)),
      at: formatVnDateTime(String(row.at)),
    }));
  }, [data]);

  async function handleExport() {
    setExportErr(null);
    setExporting(true);
    try {
      await downloadHaccpPdf();
    } catch (error) {
      setExportErr(error instanceof Error ? error.message : "Không thể xuất biên bản PDF.");
    } finally {
      setExporting(false);
    }
  }

  return (
    <div className="page-shell haccp-page">
      <PageHeader
        title="Giám sát điểm kiểm soát"
        description="Theo dõi điểm kiểm soát 1 (nguyên liệu) và điểm kiểm soát 2 (chưng cất) trong 14 ngày gần nhất."
        actions={
          <button type="button" onClick={() => void handleExport()} disabled={exporting || loading}>
            {exporting ? "Đang xuất…" : "Xuất biên bản PDF"}
          </button>
        }
      />

      {err && (
        <AlertBanner tone="danger" title="Không tải được dữ liệu" onClose={() => setErr(null)}>
          {err}
        </AlertBanner>
      )}
      {exportErr && (
        <AlertBanner tone="danger" title="Xuất file thất bại" onClose={() => setExportErr(null)}>
          {exportErr}
        </AlertBanner>
      )}

      {loading && <p className="loading-state">Đang tải dữ liệu giám sát…</p>}

      {!loading && data && (
        <>
          <div className="ops-summary">
            <div className="ops-summary__item">
              <span>Số lần kiểm nghiệm</span>
              <strong>{String(data.lab_tests ?? 0)}</strong>
            </div>
            <div
              className={`ops-summary__item${Number(data.fail_count) > 0 ? " ops-summary__item--warn" : ""}`}
            >
              <span>Số lần không đạt</span>
              <strong>{String(data.fail_count ?? 0)}</strong>
            </div>
            <div className="ops-summary__item">
              <span>Bản ghi CCP1</span>
              <strong>{ccp1.length}</strong>
            </div>
            <div className="ops-summary__item">
              <span>Bản ghi CCP2</span>
              <strong>{ccp2.length}</strong>
            </div>
          </div>

          <p className="section-description haccp-note">
            Thời gian theo giờ Việt Nam (UTC+7). Điểm kiểm soát 1 chỉ liệt kê lô nguyên liệu.
          </p>

          <section className="card haccp-section">
            <header className="ops-form-head">
              <div>
                <h2>Điểm kiểm soát 1 — Nguyên liệu</h2>
                <p>Chỉ số C14 và kết quả kiểm nghiệm lô đầu vào.</p>
              </div>
            </header>
            {ccp1.length === 0 ? (
              <EmptyState title="Chưa có bản ghi CCP1" description="Kết quả kiểm nghiệm nguyên liệu sẽ xuất hiện tại đây." />
            ) : (
              <>
                <div className="table-wrap haccp-table">
                  <table className="table">
                    <thead>
                      <tr>
                        <th>Mã lô</th>
                        <th>Chỉ số C14</th>
                        <th>Kết quả</th>
                        <th>Thời gian (VN)</th>
                      </tr>
                    </thead>
                    <tbody>
                      {ccp1.map((row) => (
                        <tr key={row.id}>
                          <td>
                            <code className="inventory-code">{row.batch_no}</code>
                          </td>
                          <td>{row.c14}</td>
                          <td>
                            <StatusBadge status={row.statusRaw} label={row.status} />
                          </td>
                          <td>{row.at}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <ul className="ops-card-list haccp-cards">
                  {ccp1.map((row) => (
                    <li key={row.id} className="ops-data-card">
                      <div className="ops-data-card__head">
                        <strong>{row.batch_no}</strong>
                        <StatusBadge status={row.statusRaw} label={row.status} />
                      </div>
                      <dl className="ops-data-card__grid">
                        <div>
                          <dt>C14</dt>
                          <dd>{row.c14}</dd>
                        </div>
                        <div>
                          <dt>Thời gian</dt>
                          <dd>{row.at}</dd>
                        </div>
                      </dl>
                    </li>
                  ))}
                </ul>
              </>
            )}
          </section>

          <section className="card haccp-section">
            <header className="ops-form-head">
              <div>
                <h2>Điểm kiểm soát 2 — Chưng cất</h2>
                <p>Nhiệt độ đỉnh và hàm lượng thành phần chính theo mẻ.</p>
              </div>
            </header>
            {ccp2.length === 0 ? (
              <EmptyState title="Chưa có bản ghi CCP2" description="Thông số vận hành chưng cất sẽ xuất hiện tại đây." />
            ) : (
              <>
                <div className="table-wrap haccp-table">
                  <table className="table">
                    <thead>
                      <tr>
                        <th>Mã mẻ</th>
                        <th>Công đoạn</th>
                        <th>Nhiệt độ đỉnh (°C)</th>
                        <th>Thành phần chính (%)</th>
                        <th>Kết quả</th>
                        <th>Thời gian (VN)</th>
                      </tr>
                    </thead>
                    <tbody>
                      {ccp2.map((row) => (
                        <tr key={row.id}>
                          <td>
                            <code className="inventory-code">{row.order_no}</code>
                          </td>
                          <td>{row.step}</td>
                          <td>{row.t_top}</td>
                          <td>{row.t_ca_percent}</td>
                          <td>
                            <StatusBadge status={row.statusRaw} label={row.status} />
                          </td>
                          <td>{row.at}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <ul className="ops-card-list haccp-cards">
                  {ccp2.map((row) => (
                    <li key={row.id} className="ops-data-card">
                      <div className="ops-data-card__head">
                        <strong>{row.order_no}</strong>
                        <StatusBadge status={row.statusRaw} label={row.status} />
                      </div>
                      <dl className="ops-data-card__grid">
                        <div>
                          <dt>Công đoạn</dt>
                          <dd>{row.step}</dd>
                        </div>
                        <div>
                          <dt>Nhiệt độ đỉnh</dt>
                          <dd>{row.t_top} °C</dd>
                        </div>
                        <div>
                          <dt>Thành phần chính</dt>
                          <dd>{row.t_ca_percent} %</dd>
                        </div>
                        <div>
                          <dt>Thời gian</dt>
                          <dd>{row.at}</dd>
                        </div>
                      </dl>
                    </li>
                  ))}
                </ul>
              </>
            )}
          </section>
        </>
      )}
    </div>
  );
}
