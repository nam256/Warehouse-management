export type PaginationProps = {
  page: number;
  pages: number;
  total: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  disabled?: boolean;
  label?: string;
};

export default function Pagination({
  page,
  pages,
  total,
  pageSize,
  onPageChange,
  disabled = false,
  label = "bản ghi",
}: PaginationProps) {
  if (total <= 0) return null;

  const from = (page - 1) * pageSize + 1;
  const to = Math.min(page * pageSize, total);

  return (
    <nav className="pagination" aria-label="Phân trang">
      <p className="pagination__summary">
        Hiển thị {from}–{to} / {total} {label}
      </p>
      <div className="pagination__controls">
        <button
          type="button"
          className="secondary"
          disabled={disabled || page <= 1}
          onClick={() => onPageChange(page - 1)}
        >
          Trước
        </button>
        <span className="pagination__page" aria-current="page">
          Trang {page}/{pages}
        </span>
        <button
          type="button"
          className="secondary"
          disabled={disabled || page >= pages}
          onClick={() => onPageChange(page + 1)}
        >
          Sau
        </button>
      </div>
    </nav>
  );
}
