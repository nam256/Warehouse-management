import { useEffect, useMemo, useRef, useState } from "react";
import {
  deleteMaterialImage,
  downloadInventoryCsv,
  downloadInventoryPdf,
  getBatches,
  getInventory,
  uploadMaterialImage,
  type QualityStatus,
  type User,
} from "../api";
import ProductThumb from "../components/ProductThumb";
import { LOAI_VAT_TU, nhan } from "../labels";
import AlertBanner from "../components/ui/AlertBanner";
import DataTable, { type DataTableColumn } from "../components/ui/DataTable";
import EmptyState from "../components/ui/EmptyState";
import FilterBar from "../components/ui/FilterBar";
import PageHeader from "../components/ui/PageHeader";
import Pagination from "../components/ui/Pagination";
import StatusBadge from "../components/ui/StatusBadge";

const PAGE_SIZE = 20;

type Row = {
  material_id: number;
  material_code: string;
  material_name: string;
  material_type: string;
  total_quantity: number;
  reserved_quantity: number;
  available_quantity: number;
  nearest_expiry: string | null;
  unit: string;
  min_stock: number;
  low_stock: boolean;
  image_url?: string | null;
  quality_statuses?: QualityStatus[];
};

type TypeFilter = "all" | "NVL" | "TP" | "BTP";
type Props = { user?: User };

function normalizeSearchText(value: string): string {
  return value
    .trim()
    .toLocaleLowerCase("vi")
    .normalize("NFD")
    .replace(/\p{M}/gu, "");
}

function formatQty(value: number): string {
  return value.toLocaleString("vi-VN", { maximumFractionDigits: 3 });
}

function formatExpiry(value: string | null, hasStock: boolean) {
  if (value) {
    const date = new Date(`${value}T00:00:00`);
    const label = date.toLocaleDateString("vi-VN");
    const expired = date.getTime() < new Date().setHours(0, 0, 0, 0);
    return (
      <span className={`inventory-expiry${expired ? " inventory-expiry--late" : ""}`}>
        {label}
        {expired ? <small>Hết hạn</small> : null}
      </span>
    );
  }
  return (
    <span className="inventory-muted">{hasStock ? "Chưa ghi hạn" : "Chưa có lô"}</span>
  );
}

function formatQuality(statuses: QualityStatus[] | undefined, hasStock: boolean) {
  if (statuses?.length) {
    return (
      <div className="status-list">
        {statuses.map((qualityStatus) => (
          <StatusBadge key={qualityStatus} status={qualityStatus} />
        ))}
      </div>
    );
  }
  return <span className="inventory-muted">{hasStock ? "Chưa có trạng thái" : "Chưa có lô"}</span>;
}

export default function Inventory({ user }: Props) {
  const [rows, setRows] = useState<Row[]>([]);
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState<TypeFilter>("all");
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [exportBusy, setExportBusy] = useState<"csv" | "pdf" | null>(null);
  const [exportMsg, setExportMsg] = useState<string | null>(null);
  const [uploadBusyId, setUploadBusyId] = useState<number | null>(null);
  const fileRefs = useRef<Record<number, HTMLInputElement | null>>({});
  const canEditImage = user?.role === "admin" || user?.role === "thu_kho" || user?.role === "ql_nm";

  function setRowImage(materialId: number, imageUrl: string | null) {
    setRows((prev) =>
      prev.map((row) => (row.material_id === materialId ? { ...row, image_url: imageUrl } : row)),
    );
  }

  async function handleImageUpload(materialId: number, file: File) {
    setError(null);
    setUploadBusyId(materialId);
    try {
      const updated = await uploadMaterialImage(materialId, file);
      setRowImage(materialId, updated.image_url ?? null);
      setExportMsg("Đã lưu ảnh sản phẩm.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không thể tải ảnh sản phẩm.");
    } finally {
      setUploadBusyId(null);
    }
  }

  async function handleImageDelete(materialId: number, materialName: string) {
    if (!window.confirm(`Xóa ảnh của “${materialName}”?`)) return;
    setError(null);
    setUploadBusyId(materialId);
    try {
      await deleteMaterialImage(materialId);
      setRowImage(materialId, null);
      setExportMsg("Đã xóa ảnh sản phẩm.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không thể xóa ảnh sản phẩm.");
    } finally {
      setUploadBusyId(null);
    }
  }

  function renderImageActions(row: Row) {
    if (!canEditImage) return null;
    const busy = uploadBusyId === row.material_id;
    const hasImage = Boolean(row.image_url);
    return (
      <div className="inventory-product__actions">
        <input
          ref={(el) => {
            fileRefs.current[row.material_id] = el;
          }}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          hidden
          onChange={(event) => {
            const file = event.target.files?.[0];
            event.target.value = "";
            if (file) void handleImageUpload(row.material_id, file);
          }}
        />
        <button
          type="button"
          className="inventory-product__link"
          disabled={busy}
          onClick={() => fileRefs.current[row.material_id]?.click()}
        >
          {busy ? "Đang lưu…" : hasImage ? "Đổi ảnh" : "Thêm ảnh"}
        </button>
        {hasImage ? (
          <>
            <span className="inventory-product__sep" aria-hidden="true">
              ·
            </span>
            <button
              type="button"
              className="inventory-product__link inventory-product__link--danger"
              disabled={busy}
              onClick={() => void handleImageDelete(row.material_id, row.material_name)}
            >
              Xóa
            </button>
          </>
        ) : null}
      </div>
    );
  }

  useEffect(() => {
    let active = true;

    async function loadInventory() {
      setError(null);
      setLoading(true);
      try {
        const [result, batches] = await Promise.all([getInventory(), getBatches()]);
        if (active) {
          setRows(
            result.map((row: Row & { material_id: number }) => ({
              ...row,
              material_id: row.material_id,
              image_url: row.image_url ?? null,
              quality_statuses: Array.from(
                new Set(
                  batches
                    .filter((batch) => batch.material_id === row.material_id)
                    .map((batch) => batch.quality_status),
                ),
              ),
            })),
          );
        }
      } catch (err) {
        if (!active) return;
        const isNetworkError =
          err instanceof TypeError || (err instanceof Error && err.message.includes("Failed to fetch"));
        setError(
          isNetworkError
            ? "Không kết nối được máy chủ. Kiểm tra backend đang chạy."
            : "Không thể tải báo cáo tồn kho. Vui lòng thử lại.",
        );
      } finally {
        if (active) setLoading(false);
      }
    }

    void loadInventory();
    return () => {
      active = false;
    };
  }, []);

  const filteredRows = useMemo(() => {
    const term = normalizeSearchText(search);
    return rows.filter((row) => {
      if (typeFilter !== "all" && row.material_type !== typeFilter) return false;
      if (!term) return true;
      return [row.material_code, row.material_name].some((value) =>
        normalizeSearchText(value ?? "").includes(term),
      );
    });
  }, [rows, search, typeFilter]);

  const summary = useMemo(() => {
    const low = rows.filter((row) => row.low_stock).length;
    const available = rows.reduce((sum, row) => sum + Number(row.available_quantity || 0), 0);
    const physical = rows.reduce((sum, row) => sum + Number(row.total_quantity || 0), 0);
    return {
      total: rows.length,
      low,
      available,
      physical,
    };
  }, [rows]);

  const pages = Math.max(1, Math.ceil(filteredRows.length / PAGE_SIZE));
  const currentPage = Math.min(page, pages);
  const pagedRows = useMemo(() => {
    const start = (currentPage - 1) * PAGE_SIZE;
    return filteredRows.slice(start, start + PAGE_SIZE);
  }, [filteredRows, currentPage]);

  useEffect(() => {
    setPage(1);
  }, [search, typeFilter]);

  async function runExport(kind: "csv" | "pdf") {
    setExportBusy(kind);
    setExportMsg(null);
    try {
      if (kind === "csv") await downloadInventoryCsv();
      else await downloadInventoryPdf();
      setExportMsg(kind === "csv" ? "Đã tải file CSV tồn kho." : "Đã tải file PDF tồn kho.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không thể xuất báo cáo tồn kho.");
    } finally {
      setExportBusy(null);
    }
  }

  const columns: DataTableColumn<Row>[] = [
    {
      key: "product",
      header: "Sản phẩm",
      className: "col-product",
      render: (row) => (
        <div className="inventory-product">
          <ProductThumb src={row.image_url} label={row.material_name} size="md" />
          <div className="inventory-product__body">
            <strong>{row.material_name}</strong>
            <span className="inventory-product__meta">
              <code className="inventory-code">{row.material_code}</code>
              <span className={`inventory-type inventory-type--${row.material_type}`}>
                {nhan(LOAI_VAT_TU, row.material_type)}
              </span>
            </span>
            {renderImageActions(row)}
          </div>
        </div>
      ),
    },
    {
      key: "stock",
      header: "Tồn khả dụng",
      className: "col-stock",
      render: (row) => (
        <div className={`inventory-stock${row.low_stock ? " inventory-stock--low" : ""}`}>
          <strong>
            {formatQty(row.available_quantity)} <span className="inventory-unit">{row.unit}</span>
          </strong>
          <span>
            Vật lý {formatQty(row.total_quantity)} · Giữ {formatQty(row.reserved_quantity)} · Min{" "}
            {formatQty(row.min_stock)}
          </span>
          <span
            className="inventory-stock-bar"
            aria-hidden="true"
            style={{
              ["--stock-ratio" as string]: `${Math.min(
                100,
                row.min_stock > 0
                  ? (row.available_quantity / row.min_stock) * 100
                  : row.available_quantity > 0
                    ? 100
                    : 0,
              )}%`,
            }}
          />
        </div>
      ),
    },
    {
      key: "expiry",
      header: "Hạn gần nhất",
      className: "col-datetime",
      render: (row) => formatExpiry(row.nearest_expiry, row.total_quantity > 0),
    },
    {
      key: "quality",
      header: "Chất lượng",
      className: "col-quality",
      render: (row) => formatQuality(row.quality_statuses, row.total_quantity > 0),
    },
    {
      key: "status",
      header: "Trạng thái",
      className: "col-status",
      render: (row) => (
        <StatusBadge
          status={row.low_stock ? "fail" : "pass"}
          label={row.low_stock ? "Tồn thấp" : "Đủ tồn"}
        />
      ),
    },
  ];

  const typeTabs: { value: TypeFilter; label: string }[] = [
    { value: "all", label: "Tất cả" },
    { value: "NVL", label: "Nguyên liệu" },
    { value: "TP", label: "Thành phẩm" },
    { value: "BTP", label: "Bán thành phẩm" },
  ];

  return (
    <div className="page-shell inventory-page">
      <PageHeader
        title="Báo cáo tồn kho"
        description="Theo dõi tồn khả dụng, hạn dùng và cảnh báo vật tư dưới mức tối thiểu."
        actions={
          <div className="inventory-export">
            <button
              type="button"
              className="secondary"
              disabled={!!exportBusy || loading}
              onClick={() => void runExport("csv")}
            >
              {exportBusy === "csv" ? "Đang xuất…" : "Xuất CSV"}
            </button>
            <button
              type="button"
              className="secondary"
              disabled={!!exportBusy || loading}
              onClick={() => void runExport("pdf")}
            >
              {exportBusy === "pdf" ? "Đang xuất…" : "Xuất PDF"}
            </button>
          </div>
        }
      />

      {!loading && rows.length > 0 && (
        <div className="inventory-summary" aria-label="Tóm tắt tồn kho">
          <article className="inventory-summary__item">
            <span>Số vật tư</span>
            <strong>{summary.total}</strong>
          </article>
          <article className={`inventory-summary__item${summary.low ? " inventory-summary__item--warn" : ""}`}>
            <span>Tồn thấp</span>
            <strong>{summary.low}</strong>
          </article>
          <article className="inventory-summary__item">
            <span>Tồn khả dụng</span>
            <strong>{formatQty(summary.available)} kg</strong>
          </article>
          <article className="inventory-summary__item">
            <span>Tồn vật lý</span>
            <strong>{formatQty(summary.physical)} kg</strong>
          </article>
        </div>
      )}

      <div className="page-tabs inventory-tabs" role="tablist" aria-label="Lọc theo loại vật tư">
        {typeTabs.map((tab) => (
          <button
            key={tab.value}
            type="button"
            role="tab"
            className={typeFilter === tab.value ? "active" : undefined}
            aria-selected={typeFilter === tab.value}
            onClick={() => setTypeFilter(tab.value)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <FilterBar ariaLabel="Tìm kiếm tồn kho">
        <label>
          Tìm kiếm sản phẩm
          <input
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Nhập mã hoặc tên (có/không dấu)"
            autoComplete="off"
            enterKeyHint="search"
          />
        </label>
      </FilterBar>

      {!loading && rows.length > 0 && (
        <p className="section-description" aria-live="polite">
          {normalizeSearchText(search) || typeFilter !== "all"
            ? `Hiển thị ${filteredRows.length}/${rows.length} vật tư`
            : `${rows.length} vật tư`}
        </p>
      )}
      {exportMsg && (
        <AlertBanner tone="success" title="Xuất báo cáo thành công" onClose={() => setExportMsg(null)}>
          {exportMsg}
        </AlertBanner>
      )}
      {error && (
        <AlertBanner tone="danger" title="Không tải được tồn kho" onClose={() => setError(null)}>
          {error}
        </AlertBanner>
      )}
      {loading && <p className="loading-state">Đang tải dữ liệu tồn kho…</p>}
      {!loading && rows.length === 0 && !error && (
        <EmptyState title="Chưa có dữ liệu tồn kho" description="Các vật tư có tồn kho sẽ xuất hiện tại đây." />
      )}
      {!loading && rows.length > 0 && filteredRows.length === 0 && (
        <EmptyState
          title="Không tìm thấy sản phẩm"
          description={`Không có vật tư phù hợp với bộ lọc hiện tại. Thử đổi loại hoặc từ khóa.`}
        />
      )}
      {pagedRows.length > 0 && (
        <>
          <div className="card table-card inventory-table">
            <DataTable
              columns={columns}
              rows={pagedRows}
              rowKey={(row) => row.material_code}
              caption="Báo cáo tồn kho vật tư"
            />
          </div>
          <div className="inventory-cards" aria-label="Danh sách tồn kho dạng thẻ">
            {pagedRows.map((row) => (
              <article
                key={row.material_code}
                className={`inventory-card${row.low_stock ? " inventory-card--low" : ""}`}
              >
                <header className="inventory-card__header">
                  <div className="inventory-card__title">
                    <ProductThumb src={row.image_url} label={row.material_name} size="md" />
                    <div className="inventory-product__body">
                      <strong>{row.material_name}</strong>
                      <p>
                        <code className="inventory-code">{row.material_code}</code>
                        <span className={`inventory-type inventory-type--${row.material_type}`}>
                          {nhan(LOAI_VAT_TU, row.material_type)}
                        </span>
                      </p>
                      {renderImageActions(row)}
                    </div>
                  </div>
                  <StatusBadge
                    status={row.low_stock ? "fail" : "pass"}
                    label={row.low_stock ? "Tồn thấp" : "Đủ tồn"}
                  />
                </header>
                <dl className="inventory-card__grid">
                  <div>
                    <dt>Khả dụng</dt>
                    <dd className={row.low_stock ? "low" : undefined}>
                      {formatQty(row.available_quantity)} {row.unit}
                    </dd>
                  </div>
                  <div>
                    <dt>Tồn vật lý</dt>
                    <dd>
                      {formatQty(row.total_quantity)} {row.unit}
                    </dd>
                  </div>
                  <div>
                    <dt>Đã giữ chỗ</dt>
                    <dd>
                      {formatQty(row.reserved_quantity)} {row.unit}
                    </dd>
                  </div>
                  <div>
                    <dt>Tồn tối thiểu</dt>
                    <dd>{formatQty(row.min_stock)}</dd>
                  </div>
                  <div>
                    <dt>Hạn gần nhất</dt>
                    <dd>{formatExpiry(row.nearest_expiry, row.total_quantity > 0)}</dd>
                  </div>
                  <div>
                    <dt>Chất lượng lô</dt>
                    <dd>{formatQuality(row.quality_statuses, row.total_quantity > 0)}</dd>
                  </div>
                </dl>
              </article>
            ))}
          </div>
          <Pagination
            page={currentPage}
            pages={pages}
            total={filteredRows.length}
            pageSize={PAGE_SIZE}
            label="vật tư"
            onPageChange={setPage}
          />
        </>
      )}
    </div>
  );
}
