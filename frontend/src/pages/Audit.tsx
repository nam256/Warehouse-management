import { useEffect, useState } from "react";
import { getAuditLogs, type User } from "../api";
import AlertBanner from "../components/ui/AlertBanner";
import DataTable, { type DataTableColumn } from "../components/ui/DataTable";
import EmptyState from "../components/ui/EmptyState";
import FilterBar from "../components/ui/FilterBar";
import PageHeader from "../components/ui/PageHeader";
import Pagination from "../components/ui/Pagination";
import { formatVnDateTime, todayVn } from "../datetime";
import { HANH_DONG_AUDIT, TEN_THUC_THE, nhan } from "../labels";
import { canWrite, roleHint } from "../roles";

type Props = { user: User };

const PAGE_SIZE = 25;

type AuditRow = {
  id: string | number;
  created_at: string;
  user_name: string;
  action: string;
  entity: string;
  ma_tham_chieu: string;
  mo_ta: string;
};

function formatDateOnly(value: string): string {
  if (!value) return "—";
  return new Date(`${value}T00:00:00`).toLocaleDateString("vi-VN");
}

export default function Audit({ user }: Props) {
  const [rows, setRows] = useState<AuditRow[]>([]);
  const [entity, setEntity] = useState("");
  const [since, setSince] = useState(todayVn());
  const [until, setUntil] = useState(todayVn());
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [pages, setPages] = useState(1);
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  async function load(overrides?: {
    since?: string;
    until?: string;
    entity?: string;
    page?: number;
  }) {
    setErr("");
    setLoading(true);
    const s = overrides?.since ?? since;
    const u = overrides?.until ?? until;
    const ent = overrides?.entity ?? entity;
    const nextPage = overrides?.page ?? page;
    try {
      const params = new URLSearchParams({
        page: String(nextPage),
        page_size: String(PAGE_SIZE),
      });
      if (ent) params.set("entity", ent);
      if (s) params.set("since", s);
      if (u) params.set("until", u);
      const data = await getAuditLogs(`?${params.toString()}`);
      setTotal(data.total);
      setPages(data.pages);
      setPage(data.page);
      setRows(
        data.items.map((r, index) => ({
          id: String(r.id ?? `${r.created_at}-${index}`),
          ...r,
          created_at: formatVnDateTime(String(r.created_at)),
          action: nhan(HANH_DONG_AUDIT, String(r.action)),
          entity: nhan(TEN_THUC_THE, String(r.entity)),
          user_name: String(r.user_name || "—"),
          ma_tham_chieu: String(r.entity_id || "—"),
          mo_ta: String(r.detail || "—"),
        })) as AuditRow[],
      );
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Có lỗi xảy ra");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (canWrite(user, "audit")) void load({ page: 1 });
    // eslint-disable-next-line react-hooks/exhaustive-deps -- chỉ tải lại khi đổi user
  }, [user]);

  if (!canWrite(user, "audit")) {
    return (
      <div className="page-shell audit-page">
        <PageHeader
          title="Nhật ký thao tác hệ thống"
          description="Theo dõi thay đổi dữ liệu quan trọng trong hệ thống."
        />
        <AlertBanner tone="warning" title="Không có quyền truy cập">
          {roleHint("audit")}
        </AlertBanner>
      </div>
    );
  }

  const columns: DataTableColumn<AuditRow>[] = [
    { key: "created_at", header: "Thời gian (VN)", className: "col-datetime", render: (row) => row.created_at },
    { key: "user_name", header: "Người thực hiện", render: (row) => <strong>{row.user_name}</strong> },
    { key: "action", header: "Hành động", render: (row) => row.action },
    { key: "entity", header: "Loại dữ liệu", render: (row) => row.entity },
    { key: "reference", header: "Mã tham chiếu", className: "col-code", render: (row) => row.ma_tham_chieu },
    { key: "description", header: "Mô tả", className: "col-description", render: (row) => row.mo_ta },
  ];

  return (
    <div className="page-shell audit-page">
      <PageHeader
        title="Nhật ký thao tác hệ thống"
        description="Thời gian theo giờ Việt Nam (UTC+7). Hệ thống chỉ ghi các thao tác thay đổi dữ liệu."
      />

      <div className="ops-summary">
        <div className="ops-summary__item">
          <span>Tổng bản ghi</span>
          <strong>{total.toLocaleString("vi-VN")}</strong>
        </div>
        <div className="ops-summary__item">
          <span>Trang hiện tại</span>
          <strong>
            {page}/{pages}
          </strong>
        </div>
        <div className="ops-summary__item">
          <span>Khoảng lọc</span>
          <strong>
            {since && until ? `${formatDateOnly(since)}–${formatDateOnly(until)}` : "Tất cả"}
          </strong>
        </div>
      </div>

      <FilterBar ariaLabel="Bộ lọc nhật ký thao tác">
        <label>
          Từ ngày
          <input type="date" value={since} onChange={(e) => setSince(e.target.value)} />
        </label>
        <label>
          Đến ngày
          <input type="date" value={until} onChange={(e) => setUntil(e.target.value)} />
        </label>
        <label>
          Loại dữ liệu
          <select value={entity} onChange={(e) => setEntity(e.target.value)}>
            <option value="">Tất cả loại dữ liệu</option>
            {Object.entries(TEN_THUC_THE).map(([key, label]) => (
              <option key={key} value={key}>
                {label}
              </option>
            ))}
          </select>
        </label>
        <button
          type="button"
          disabled={loading}
          onClick={() => {
            setPage(1);
            void load({ page: 1 });
          }}
        >
          {loading ? "Đang tải…" : "Áp dụng bộ lọc"}
        </button>
        <button
          type="button"
          className="secondary"
          disabled={loading}
          onClick={() => {
            setSince("");
            setUntil("");
            setEntity("");
            setPage(1);
            void load({ since: "", until: "", entity: "", page: 1 });
          }}
        >
          Xóa lọc
        </button>
      </FilterBar>
      {err && (
        <AlertBanner tone="danger" title="Không tải được nhật ký" onClose={() => setErr("")}>
          {err}
        </AlertBanner>
      )}
      {loading && <p className="loading-state">Đang tải nhật ký thao tác…</p>}
      {!loading && !err && rows.length === 0 && (
        <EmptyState
          title="Không có nhật ký phù hợp"
          description="Thử thay đổi khoảng ngày hoặc loại dữ liệu trong bộ lọc."
        />
      )}
      {rows.length > 0 && (
        <>
          <div className="card table-card">
            <DataTable
              columns={columns}
              rows={rows}
              rowKey={(row) => row.id}
              caption="Nhật ký thao tác hệ thống"
            />
          </div>
          <ul className="ops-card-list audit-cards">
            {rows.map((row) => (
              <li key={row.id} className="ops-data-card">
                <div className="ops-data-card__head">
                  <strong>{row.user_name}</strong>
                  <span>{row.created_at}</span>
                </div>
                <dl className="ops-data-card__grid">
                  <div>
                    <dt>Hành động</dt>
                    <dd>{row.action}</dd>
                  </div>
                  <div>
                    <dt>Loại dữ liệu</dt>
                    <dd>{row.entity}</dd>
                  </div>
                  <div className="full">
                    <dt>Mô tả</dt>
                    <dd>{row.mo_ta}</dd>
                  </div>
                </dl>
              </li>
            ))}
          </ul>
          <Pagination
            page={page}
            pages={pages}
            total={total}
            pageSize={PAGE_SIZE}
            disabled={loading}
            label="thao tác"
            onPageChange={(next) => void load({ page: next })}
          />
        </>
      )}
    </div>
  );
}
