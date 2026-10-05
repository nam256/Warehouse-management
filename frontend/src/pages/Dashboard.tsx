import { useEffect, useState } from "react";
import { getDashboard } from "../api";
import AlertBanner from "../components/ui/AlertBanner";
import EmptyState from "../components/ui/EmptyState";
import PageHeader from "../components/ui/PageHeader";
import StatusBadge from "../components/ui/StatusBadge";

type DashCard = {
  id: string;
  label: string;
  hint: string;
  value: string | number;
  danger?: boolean;
  badge?: boolean;
};

type DashGroup = {
  id: string;
  title: string;
  tone: "stock" | "quality" | "production" | "capa";
  cards: DashCard[];
};

export default function Dashboard() {
  const [data, setData] = useState<Record<string, number> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function loadDashboard() {
      setError(null);
      setLoading(true);
      try {
        const result = await getDashboard();
        if (active) setData(result);
      } catch (err) {
        if (!active) return;
        const isNetworkError =
          err instanceof TypeError || (err instanceof Error && err.message.includes("Failed to fetch"));
        setError(
          isNetworkError
            ? "Không kết nối được máy chủ. Kiểm tra backend đang chạy."
            : "Không thể tải dữ liệu tổng quan. Vui lòng thử lại.",
        );
      } finally {
        if (active) setLoading(false);
      }
    }

    void loadDashboard();
    return () => {
      active = false;
    };
  }, []);

  const groups: DashGroup[] = data
    ? [
        {
          id: "stock",
          title: "Tồn kho",
          tone: "stock",
          cards: [
            {
              id: "materials",
              label: "Loại vật tư",
              hint: "Đang quản lý",
              value: data.material_count,
            },
            {
              id: "batches",
              label: "Lô hàng",
              hint: "Trong kho",
              value: data.batch_count,
            },
            {
              id: "total",
              label: "Tổng tồn",
              hint: "Kilogram",
              value: data.total_stock_kg.toFixed(1),
            },
            {
              id: "low",
              label: "Tồn thấp",
              hint: "Dưới mức tối thiểu",
              value: data.low_stock_items,
              danger: true,
            },
          ],
        },
        {
          id: "quality",
          title: "Chất lượng",
          tone: "quality",
          cards: [
            {
              id: "ccp1-pending",
              label: "Chờ kiểm tra",
              hint: "Điểm kiểm soát 1 · nguyên liệu",
              value: data.ccp_pending,
            },
            {
              id: "ccp1-fail",
              label: "Không đạt",
              hint: "Điểm kiểm soát 1 · nguyên liệu",
              value: data.ccp_fail,
              danger: true,
            },
            {
              id: "ccp2-fail",
              label: "Không đạt",
              hint: "Điểm kiểm soát 2 · chưng cất",
              value: data.ccp2_fail ?? 0,
              danger: true,
            },
          ],
        },
        {
          id: "production",
          title: "Sản xuất",
          tone: "production",
          cards: [
            {
              id: "running",
              label: "Đang chạy",
              hint: "Mẻ sản xuất",
              value: data.orders_running ?? 0,
            },
            {
              id: "done",
              label: "Hoàn thành",
              hint: "Mẻ sản xuất",
              value: data.orders_done ?? 0,
            },
          ],
        },
        {
          id: "capa",
          title: "Khắc phục",
          tone: "capa",
          cards: [
            {
              id: "overdue",
              label: "Quá hạn",
              hint: "Hành động khắc phục",
              value: data.overdue_capa_count ?? 0,
              danger: (data.overdue_capa_count ?? 0) > 0,
              badge: true,
            },
          ],
        },
      ]
    : [];

  return (
    <>
      <PageHeader
        title="Bảng tổng quan"
        description="Theo dõi nhanh tồn kho, sản xuất và các điểm kiểm soát chất lượng."
        actions={
          <StatusBadge status={error ? "fail" : "pass"} label={error ? "Mất kết nối" : "Dữ liệu hiện hành"} />
        }
      />
      {error && (
        <AlertBanner tone="danger" title="Không tải được dữ liệu" onClose={() => setError(null)}>
          {error}
        </AlertBanner>
      )}
      {loading && <p className="loading-state">Đang tải dữ liệu tổng quan…</p>}
      {!loading && !data && (
        <EmptyState
          title="Chưa có dữ liệu tổng quan"
          description="Dữ liệu sẽ hiển thị sau khi kết nối lại với máy chủ."
        />
      )}
      {data && (
        <div className="dash-groups">
          {groups.map((group) => (
            <section className={`dash-group dash-group--${group.tone}`} key={group.id} aria-labelledby={`dash-${group.id}`}>
              <header className="dash-group__head">
                <span className="dash-group__mark" aria-hidden="true" />
                <h2 id={`dash-${group.id}`}>{group.title}</h2>
              </header>
              <div className="grid dash-group__grid">
                {group.cards.map((card) => (
                  <article
                    className={`card stat-card stat-card--${group.tone}${card.danger ? " stat-card--danger" : ""}`}
                    key={card.id}
                  >
                    <p className="stat-card__hint">{card.hint}</p>
                    <div className="stat-card__label">{card.label}</div>
                    <div className={`stat stat-card__value${card.danger ? " low" : ""}`}>
                      {card.badge ? (
                        <StatusBadge
                          status={card.danger ? "overdue" : "closed"}
                          label={`${card.value} hồ sơ`}
                        />
                      ) : (
                        card.value
                      )}
                    </div>
                  </article>
                ))}
              </div>
            </section>
          ))}
        </div>
      )}
    </>
  );
}
