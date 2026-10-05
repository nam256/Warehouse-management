import { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  getCorrectiveActions,
  transitionCorrectiveAction,
  type CapaDisposition,
  type CapaScope,
  type CapaStatus,
  type CorrectiveAction,
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

const TABS: { value: CapaScope; label: string }[] = [
  { value: "open", label: "Đang mở" },
  { value: "overdue", label: "Quá hạn" },
  { value: "closed", label: "Đã đóng" },
];

const DISPOSITIONS: { value: CapaDisposition; label: string }[] = [
  { value: "retest", label: "Kiểm nghiệm lại" },
  { value: "rework", label: "Tái xử lý" },
  { value: "reject", label: "Loại bỏ" },
  { value: "use_as_is", label: "Chấp nhận sử dụng" },
];

function errorMessage(error: unknown, fallback: string) {
  if (error instanceof TypeError || (error instanceof Error && error.message.includes("Failed to fetch"))) {
    return "Không kết nối được máy chủ. Kiểm tra backend đang chạy.";
  }
  return error instanceof Error && error.message ? error.message : fallback;
}

function sourceRoute(item: CorrectiveAction) {
  const kind = item.source_type || item.entity_type;
  if (kind === "lab_test") return "/lab";
  if (kind === "operation_record") return "/production";
  if (kind === "stock_batch" || kind === "quality_rejection") return "/quality";
  if (kind === "inventory" || kind === "system") return "/inventory";
  return "/capa";
}

function sourceLabel(item: CorrectiveAction) {
  const labels: Record<string, string> = {
    lab_test: "Kiểm nghiệm",
    operation_record: "Vận hành CCP2",
    stock_batch: "Lô chất lượng",
    quality_rejection: "Từ chối chất lượng",
    inventory: "Tồn kho",
    system: "Tồn kho",
  };
  const key = item.source_type || item.entity_type || "";
  const name = labels[key] ?? "Khác";
  const id = item.source_id ?? item.entity_id;
  if (!id) return name;
  return `${name} #${id}`;
}

function isOverdue(item: CorrectiveAction) {
  return Boolean(
    item.status !== "closed" &&
      item.due_date &&
      new Date(`${item.due_date}T23:59:59`).getTime() < Date.now(),
  );
}

function nextStatus(status: CapaStatus): CapaStatus | null {
  const next: Partial<Record<CapaStatus, CapaStatus>> = {
    open: "investigating",
    investigating: "action_pending",
    action_pending: "verification",
    verification: "closed",
  };
  return next[status] ?? null;
}

function actionLabel(status: CapaStatus) {
  return {
    investigating: "Bắt đầu điều tra",
    action_pending: "Ghi nhận hành động",
    verification: "Xác minh CAPA",
    closed: "Đóng CAPA",
    open: "Mở CAPA",
  }[status];
}

export default function Capa({ user }: Props) {
  const [scope, setScope] = useState<CapaScope>("open");
  const [search, setSearch] = useState("");
  const [rows, setRows] = useState<CorrectiveAction[]>([]);
  const [selected, setSelected] = useState<CorrectiveAction | null>(null);
  const [rootCause, setRootCause] = useState("");
  const [actionTaken, setActionTaken] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [disposition, setDisposition] = useState<CapaDisposition>("reject");
  const [verificationNote, setVerificationNote] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const loadActions = useCallback(async () => {
    setError(null);
    setLoading(true);
    try {
      setRows(await getCorrectiveActions(scope));
    } catch (error) {
      setError(errorMessage(error, "Không thể tải danh sách CAPA."));
    } finally {
      setLoading(false);
    }
  }, [scope]);

  useEffect(() => {
    void loadActions();
  }, [loadActions]);

  function selectAction(item: CorrectiveAction) {
    setSelected(item);
    setRootCause(item.root_cause ?? "");
    setActionTaken(item.action_taken ?? "");
    setDueDate(item.due_date ?? "");
    setDisposition(item.disposition ?? "reject");
    setVerificationNote(item.verification_note ?? "");
    setError(null);
    setSuccess(null);
  }

  const filteredRows = useMemo(() => {
    const term = search.trim().toLocaleLowerCase("vi");
    if (!term) return rows;
    return rows.filter((item) =>
      [item.title, item.reason, sourceLabel(item)].some((value) =>
        value?.toLocaleLowerCase("vi").includes(term),
      ),
    );
  }, [rows, search]);

  const summary = useMemo(() => {
    const open = filteredRows.filter((item) => item.status !== "closed").length;
    const overdue = filteredRows.filter((item) => isOverdue(item)).length;
    const closed = filteredRows.filter((item) => item.status === "closed").length;
    return { open, overdue, closed };
  }, [filteredRows]);

  const canInvestigate = ["lab", "ky_thuat", "admin"].includes(user.role);
  const canVerify = ["attp", "admin"].includes(user.role);
  const target = selected ? nextStatus(selected.status) : null;
  const canTransition =
    Boolean(target) &&
    (selected?.status === "open" || selected?.status === "investigating" ? canInvestigate : canVerify);

  async function submitTransition() {
    if (!selected || !target) return;
    setError(null);
    setSuccess(null);
    setBusy(true);
    try {
      await transitionCorrectiveAction(selected.id, {
        to_status: target,
        root_cause: rootCause,
        action_taken: actionTaken,
        due_date: dueDate || undefined,
        disposition,
        verification_note: verificationNote,
      });
      setSuccess(`Đã chuyển CAPA #${selected.id} sang trạng thái mới.`);
      setSelected(null);
      await loadActions();
    } catch (error) {
      setError(errorMessage(error, "Không thể cập nhật CAPA."));
    } finally {
      setBusy(false);
    }
  }

  const columns = useMemo<DataTableColumn<CorrectiveAction>[]>(
    () => [
      {
        key: "title",
        header: "Hồ sơ",
        render: (item) => (
          <>
            <strong>{item.title ?? `Hồ sơ #${item.id}`}</strong>
            <div>{item.reason}</div>
          </>
        ),
      },
      {
        key: "source",
        header: "Nguồn",
        render: (item) => <Link to={sourceRoute(item)}>{sourceLabel(item)}</Link>,
      },
      {
        key: "status",
        header: "Trạng thái",
        render: (item) => (
          <ActionBar align="start">
            <StatusBadge status={item.status} />
            {isOverdue(item) && <StatusBadge status="overdue" />}
          </ActionBar>
        ),
      },
      { key: "due", header: "Hạn xử lý", render: (item) => item.due_date ?? "Chưa đặt" },
      { key: "root", header: "Nguyên nhân gốc", render: (item) => item.root_cause ?? "—" },
      { key: "action", header: "Hành động", render: (item) => item.action_taken ?? "—" },
      {
        key: "disposition",
        header: "Disposition",
        render: (item) =>
          DISPOSITIONS.find((entry) => entry.value === item.disposition)?.label ?? "—",
      },
      {
        key: "manage",
        header: "Thao tác",
        render: (item) => (
          <button type="button" className="secondary" onClick={() => selectAction(item)}>
            {item.status === "closed" ? "Xem hồ sơ" : "Xử lý"}
          </button>
        ),
      },
    ],
    [],
  );

  return (
    <div className="page-shell capa-page">
      <PageHeader
        title="Quản lý khắc phục sai lệch"
        description="Theo dõi sai lệch CCP từ điều tra, hành động khắc phục đến xác minh và đóng hồ sơ."
        actions={<StatusBadge status={scope === "overdue" ? "overdue" : scope === "closed" ? "closed" : "open"} />}
      />

      <div className="ops-summary">
        <div className="ops-summary__item">
          <span>Đang mở</span>
          <strong>{summary.open}</strong>
        </div>
        <div className={`ops-summary__item${summary.overdue > 0 ? " ops-summary__item--warn" : ""}`}>
          <span>Quá hạn</span>
          <strong>{summary.overdue}</strong>
        </div>
        <div className="ops-summary__item">
          <span>Đã đóng</span>
          <strong>{summary.closed}</strong>
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
      <div className="page-tabs capa-tabs" role="tablist" aria-label="Lọc hồ sơ CAPA theo trạng thái">
        {TABS.map((tab) => (
          <button
            type="button"
            role="tab"
            key={tab.value}
            className={scope === tab.value ? "active" : undefined}
            aria-selected={scope === tab.value}
            onClick={() => {
              setScope(tab.value);
              setSelected(null);
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <FilterBar ariaLabel="Tìm kiếm hồ sơ CAPA">
        <label>
          Tìm kiếm
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Tên, lý do hoặc nguồn sai lệch"
          />
        </label>
      </FilterBar>
      {loading && <p className="loading-state">Đang tải hồ sơ CAPA…</p>}
      {!loading && filteredRows.length === 0 && (
        <EmptyState
          title="Không có hồ sơ CAPA phù hợp"
          description="Hồ sơ sẽ tự động xuất hiện khi CCP không đạt hoặc ATTP từ chối lô."
        />
      )}
      {filteredRows.length > 0 && (
        <>
          <div className="card table-wrap">
            <DataTable columns={columns} rows={filteredRows} rowKey={(item) => item.id} caption="Danh sách CAPA" />
          </div>
          <ul className="ops-card-list capa-cards">
            {filteredRows.map((item) => (
              <li key={item.id} className="ops-data-card">
                <div className="ops-data-card__head">
                  <strong>{item.title ?? `Hồ sơ #${item.id}`}</strong>
                  <div className="status-list">
                    <StatusBadge status={item.status} />
                    {isOverdue(item) && <StatusBadge status="overdue" />}
                  </div>
                </div>
                <dl className="ops-data-card__grid">
                  <div>
                    <dt>Hạn xử lý</dt>
                    <dd>{item.due_date ?? "Chưa đặt"}</dd>
                  </div>
                  <div>
                    <dt>Nguồn</dt>
                    <dd>
                      <Link to={sourceRoute(item)}>{sourceLabel(item)}</Link>
                    </dd>
                  </div>
                  <div className="full">
                    <dt>Lý do</dt>
                    <dd>{item.reason}</dd>
                  </div>
                </dl>
                <ActionBar align="start">
                  <button type="button" className="secondary" onClick={() => selectAction(item)}>
                    {item.status === "closed" ? "Xem hồ sơ" : "Xử lý"}
                  </button>
                </ActionBar>
              </li>
            ))}
          </ul>
        </>
      )}
      {selected && (
        <section className="card form-panel wide capa-detail">
          <header className="ops-form-head">
            <div>
              <h2>{selected.title ?? `CAPA #${selected.id}`}</h2>
              <p>
                <StatusBadge status={selected.status} /> — {sourceLabel(selected)}
              </p>
            </div>
          </header>
          <div className="form-grid">
            <label className="full">
              Nguyên nhân gốc
              <textarea value={rootCause} onChange={(event) => setRootCause(event.target.value)} disabled={busy || selected.status === "closed"} />
            </label>
            <label className="full">
              Hành động khắc phục
              <textarea value={actionTaken} onChange={(event) => setActionTaken(event.target.value)} disabled={busy || selected.status === "closed"} />
            </label>
            <label>
              Hạn xử lý
              <input type="date" value={dueDate} onChange={(event) => setDueDate(event.target.value)} disabled={busy || selected.status === "closed"} />
            </label>
            <label>
              Disposition
              <select value={disposition} onChange={(event) => setDisposition(event.target.value as CapaDisposition)} disabled={busy || selected.status === "closed"}>
                {DISPOSITIONS.filter((item) => item.value !== "use_as_is" || user.role === "attp").map((item) => (
                  <option key={item.value} value={item.value}>
                    {item.label}
                  </option>
                ))}
              </select>
            </label>
            <label className="full">
              Xác minh / justification khi chấp nhận sử dụng
              <textarea
                value={verificationNote}
                onChange={(event) => setVerificationNote(event.target.value)}
                disabled={busy || selected.status === "closed"}
              />
            </label>
          </div>
          <ActionBar align="between">
            <button type="button" className="secondary" disabled={busy} onClick={() => setSelected(null)}>
              Đóng hồ sơ xem
            </button>
            {canTransition && target && (
              <button type="button" disabled={busy} onClick={() => void submitTransition()}>
                {busy ? "Đang cập nhật…" : actionLabel(target)}
              </button>
            )}
          </ActionBar>
          {!canTransition && selected.status !== "closed" && (
            <AlertBanner tone="info">
              Vai trò hiện tại không được thực hiện bước chuyển trạng thái tiếp theo.
            </AlertBanner>
          )}
        </section>
      )}
    </div>
  );
}
