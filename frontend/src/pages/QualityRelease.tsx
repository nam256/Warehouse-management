import { useCallback, useEffect, useMemo, useState } from "react";
import {
  downloadReleaseCertificate,
  getQualityBatchHistory,
  getQualityBatches,
  transitionQualityBatch,
  type BatchStatusHistory,
  type QualityBatch,
  type QualityStatus,
  type User,
} from "../api";
import ActionBar from "../components/ui/ActionBar";
import AlertBanner from "../components/ui/AlertBanner";
import DataTable, { type DataTableColumn } from "../components/ui/DataTable";
import EmptyState from "../components/ui/EmptyState";
import FilterBar from "../components/ui/FilterBar";
import PageHeader from "../components/ui/PageHeader";
import StatusBadge from "../components/ui/StatusBadge";

type Props = { user: User };

const STATUSES: { value: QualityStatus | ""; label: string }[] = [
  { value: "", label: "Tất cả trạng thái" },
  { value: "quarantine", label: "Chờ xử lý" },
  { value: "sampling", label: "Đang lấy mẫu" },
  { value: "under_test", label: "Đang kiểm nghiệm" },
  { value: "awaiting_release", label: "Chờ phê duyệt" },
  { value: "released", label: "Đã giải phóng" },
  { value: "rejected", label: "Từ chối" },
  { value: "retest", label: "Kiểm nghiệm lại" },
];

function errorMessage(error: unknown, fallback: string) {
  if (error instanceof TypeError || (error instanceof Error && error.message.includes("Failed to fetch"))) {
    return "Không kết nối được máy chủ. Kiểm tra backend đang chạy.";
  }
  return error instanceof Error && error.message ? error.message : fallback;
}

function nextActions(role: string, batch: QualityBatch) {
  const status = batch.quality_status;
  const actions: { status: QualityStatus; label: string; disabled?: boolean; title?: string }[] = [];
  if (role === "lab" || role === "admin") {
    if (status === "quarantine") actions.push({ status: "sampling", label: "Bắt đầu lấy mẫu" });
    if (status === "sampling") actions.push({ status: "under_test", label: "Bắt đầu kiểm nghiệm" });
    if (status === "under_test") {
      if (batch.ccp1_status === "pass") {
        actions.push({ status: "awaiting_release", label: "Gửi Bộ phận an toàn thực phẩm phê duyệt" });
      } else {
        actions.push({
          status: "awaiting_release",
          label: "Gửi Bộ phận an toàn thực phẩm phê duyệt",
          disabled: true,
          title:
            batch.ccp1_status === "fail"
              ? "Lô điểm kiểm soát 1 không đạt — không thể gửi phê duyệt. Hãy kiểm nghiệm lại hoặc từ chối."
              : "Lô chưa đạt điểm kiểm soát 1 — cần Phòng kiểm nghiệm nhập kết quả đạt trước khi gửi Bộ phận an toàn thực phẩm.",
        });
      }
      actions.push({ status: "retest", label: "Yêu cầu kiểm nghiệm lại" });
      actions.push({ status: "rejected", label: "Từ chối lô" });
    }
    if (status === "retest") actions.push({ status: "under_test", label: "Kiểm nghiệm lại" });
  }
  if ((role === "attp" || role === "admin") && status === "awaiting_release") {
    actions.push({ status: "released", label: "Giải phóng lô" });
    actions.push({ status: "rejected", label: "Từ chối lô" });
  }
  return actions;
}

export default function QualityRelease({ user }: Props) {
  const [rows, setRows] = useState<QualityBatch[]>([]);
  const [history, setHistory] = useState<BatchStatusHistory[]>([]);
  const [selected, setSelected] = useState<QualityBatch | null>(null);
  const [status, setStatus] = useState<QualityStatus | "">("");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const loadBatches = useCallback(async () => {
    setError(null);
    setLoading(true);
    try {
      setRows(await getQualityBatches(status, search));
    } catch (error) {
      setError(errorMessage(error, "Không thể tải danh sách lô chất lượng."));
    } finally {
      setLoading(false);
    }
  }, [search, status]);

  useEffect(() => {
    void loadBatches();
  }, [loadBatches]);

  const summary = useMemo(() => {
    const awaiting = rows.filter((row) => row.quality_status === "awaiting_release").length;
    const released = rows.filter((row) => row.quality_status === "released").length;
    const rejected = rows.filter((row) => row.quality_status === "rejected").length;
    return { total: rows.length, awaiting, released, rejected };
  }, [rows]);

  async function showHistory(batch: QualityBatch) {
    setError(null);
    setBusyId(batch.id);
    try {
      setSelected(batch);
      setHistory(await getQualityBatchHistory(batch.id));
    } catch (error) {
      setError(errorMessage(error, "Không thể tải lịch sử trạng thái lô."));
    } finally {
      setBusyId(null);
    }
  }

  async function transition(batch: QualityBatch, toStatus: QualityStatus) {
    if (toStatus === "awaiting_release" && batch.ccp1_status !== "pass") {
      setError(
        batch.ccp1_status === "fail"
          ? `Lô ${batch.batch_no} điểm kiểm soát 1 không đạt — không thể gửi Bộ phận an toàn thực phẩm. Hãy kiểm nghiệm lại hoặc từ chối lô.`
          : `Lô ${batch.batch_no} chưa đạt điểm kiểm soát 1 — Phòng kiểm nghiệm cần nhập kết quả đạt trước khi gửi phê duyệt.`,
      );
      return;
    }
    const approvalAction = toStatus === "released" || toStatus === "rejected";
    let note = "Thao tác trên bảng phê duyệt chất lượng";
    if (approvalAction) {
      const enteredNote = window.prompt("Nhập lý do phê duyệt/từ chối lô:");
      if (enteredNote === null) return;
      if (!enteredNote.trim()) {
        setError("Vui lòng nhập lý do trước khi xác nhận điện tử.");
        return;
      }
      if (!window.confirm(`Xác nhận điện tử quyết định cho lô ${batch.batch_no}?`)) return;
      note = enteredNote.trim();
    }
    setError(null);
    setSuccess(null);
    setBusyId(batch.id);
    try {
      await transitionQualityBatch(
        batch.id,
        toStatus,
        toStatus === "rejected" ? "REJECT" : "M1_WORKFLOW",
        note,
      );
      setSuccess(`Đã cập nhật trạng thái lô ${batch.batch_no}.`);
      await loadBatches();
      if (selected?.id === batch.id) {
        setHistory(await getQualityBatchHistory(batch.id));
      }
    } catch (error) {
      setError(errorMessage(error, "Không thể cập nhật trạng thái lô."));
    } finally {
      setBusyId(null);
    }
  }

  async function downloadCertificate(batch: QualityBatch) {
    setError(null);
    setBusyId(batch.id);
    try {
      await downloadReleaseCertificate(batch.id, batch.batch_no);
    } catch (error) {
      setError(errorMessage(error, "Không thể tải chứng nhận giải phóng lô."));
    } finally {
      setBusyId(null);
    }
  }

  function renderRowActions(row: QualityBatch) {
    return (
      <ActionBar align="start">
        <button type="button" className="secondary" disabled={busyId === row.id} onClick={() => void showHistory(row)}>
          Lịch sử
        </button>
        {nextActions(user.role, row).map((action) => (
          <button
            type="button"
            key={action.status + action.label}
            disabled={busyId === row.id || Boolean(action.disabled)}
            title={action.title}
            onClick={() => void transition(row, action.status)}
          >
            {action.label}
          </button>
        ))}
        {row.has_release_certificate && (
          <button type="button" disabled={busyId === row.id} onClick={() => void downloadCertificate(row)}>
            Tải chứng nhận
          </button>
        )}
        {row.quality_status === "released" && !row.has_release_certificate && (
          <span className="muted" title="Cần phê duyệt lại để có chữ ký Bộ phận an toàn thực phẩm">
            Chưa có chứng nhận
          </span>
        )}
      </ActionBar>
    );
  }

  const columns = useMemo<DataTableColumn<QualityBatch>[]>(
    () => [
      { key: "batch", header: "Mã lô", className: "col-code", render: (row) => <strong>{row.batch_no}</strong> },
      { key: "quantity", header: "Tồn", className: "col-number", render: (row) => `${row.quantity} kg` },
      { key: "ccp1", header: "CCP1", render: (row) => <StatusBadge status={row.ccp1_status} /> },
      { key: "quality", header: "Chất lượng", render: (row) => <StatusBadge status={row.quality_status} /> },
      { key: "expiry", header: "Hạn dùng", className: "col-datetime", render: (row) => row.expiry_date ?? "—" },
      {
        key: "actions",
        header: "Thao tác",
        className: "actions",
        render: (row) => renderRowActions(row),
      },
    ],
    [busyId, selected?.id, user.role],
  );

  return (
    <div className="page-shell quality-page">
      <PageHeader
        title="Phê duyệt chất lượng lô"
        description="Theo dõi lô từ cách ly, kiểm nghiệm đến phê duyệt giải phóng độc lập bởi Bộ phận an toàn thực phẩm."
      />

      <div className="ops-summary">
        <div className="ops-summary__item">
          <span>Số lô hiển thị</span>
          <strong>{summary.total}</strong>
        </div>
        <div className={`ops-summary__item${summary.awaiting > 0 ? " ops-summary__item--warn" : ""}`}>
          <span>Chờ phê duyệt</span>
          <strong>{summary.awaiting}</strong>
        </div>
        <div className="ops-summary__item">
          <span>Đã giải phóng</span>
          <strong>{summary.released}</strong>
        </div>
        <div className="ops-summary__item">
          <span>Từ chối</span>
          <strong>{summary.rejected}</strong>
        </div>
      </div>

      {error && (
        <AlertBanner tone="danger" title="Không thể thực hiện thao tác" onClose={() => setError(null)}>
          {error}
        </AlertBanner>
      )}
      {success && (
        <AlertBanner tone="success" title="Cập nhật thành công" onClose={() => setSuccess(null)}>
          {success}
        </AlertBanner>
      )}
      <FilterBar>
        <label>
          Tìm theo mã lô
          <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Ví dụ: NVL-2026" />
        </label>
        <label>
          Trạng thái
          <select value={status} onChange={(event) => setStatus(event.target.value as QualityStatus | "")}>
            {STATUSES.map((item) => (
              <option key={item.value || "all"} value={item.value}>
                {item.label}
              </option>
            ))}
          </select>
        </label>
      </FilterBar>
      {loading && <p className="loading-state">Đang tải danh sách lô…</p>}
      {!loading && rows.length === 0 && (
        <EmptyState title="Không có lô phù hợp" description="Thay đổi bộ lọc hoặc nhập kho một lô mới để bắt đầu." />
      )}
      {rows.length > 0 && (
        <>
          <div className="card table-wrap">
            <DataTable columns={columns} rows={rows} rowKey={(row) => row.id} caption="Danh sách giữ–giải phóng" />
          </div>
          <ul className="ops-card-list quality-cards">
            {rows.map((row) => (
              <li key={row.id} className="ops-data-card">
                <div className="ops-data-card__head">
                  <strong>{row.batch_no}</strong>
                  <StatusBadge status={row.quality_status} />
                </div>
                <dl className="ops-data-card__grid">
                  <div>
                    <dt>Tồn</dt>
                    <dd>{row.quantity} kg</dd>
                  </div>
                  <div>
                    <dt>Điểm kiểm soát 1</dt>
                    <dd>
                      <StatusBadge status={row.ccp1_status} />
                    </dd>
                  </div>
                  <div>
                    <dt>Hạn dùng</dt>
                    <dd>{row.expiry_date ?? "—"}</dd>
                  </div>
                </dl>
                {renderRowActions(row)}
              </li>
            ))}
          </ul>
        </>
      )}
      {selected && (
        <section className="card quality-history">
          <header className="ops-form-head">
            <div>
              <h2>Lịch sử lô {selected.batch_no}</h2>
              <p>Các lần chuyển trạng thái, lý do và thời gian xử lý.</p>
            </div>
          </header>
          {history.length === 0 ? (
            <EmptyState title="Chưa có lịch sử" description="Lô chưa thực hiện chuyển trạng thái." />
          ) : (
            <DataTable
              columns={[
                {
                  key: "change",
                  header: "Chuyển trạng thái",
                  render: (item: BatchStatusHistory) => (
                    <>
                      {item.from_status ? <StatusBadge status={item.from_status} /> : "Khởi tạo"} →{" "}
                      <StatusBadge status={item.to_status} />
                    </>
                  ),
                },
                { key: "reason", header: "Lý do", render: (item: BatchStatusHistory) => item.reason ?? "—" },
                { key: "note", header: "Ghi chú", render: (item: BatchStatusHistory) => item.note ?? "—" },
                {
                  key: "time",
                  header: "Thời gian",
                  render: (item: BatchStatusHistory) => new Date(item.changed_at).toLocaleString("vi-VN"),
                },
              ]}
              rows={history}
              rowKey={(item) => item.id}
              caption={`Lịch sử trạng thái lô ${selected.batch_no}`}
            />
          )}
        </section>
      )}
    </div>
  );
}
