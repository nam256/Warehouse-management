import { useCallback, useEffect, useMemo, useState } from "react";
import {
  addOperation,
  approveProductionOrder,
  cancelProductionOrder,
  completeProductionOrder,
  createProductionOrder,
  getMaterials,
  getProductionOrders,
  getProductionReservations,
  startProductionOrder,
  type MaterialReservation,
  type User,
} from "../api";
import ActionBar from "../components/ui/ActionBar";
import AlertBanner from "../components/ui/AlertBanner";
import EmptyState from "../components/ui/EmptyState";
import PageHeader from "../components/ui/PageHeader";
import StatusBadge from "../components/ui/StatusBadge";
import { canWrite, roleHint } from "../roles";
import { shortRef, sortByRef } from "../shortRef";

type Order = {
  id: number;
  order_no: string;
  product_code: string;
  planned_qty: number;
  status: string;
  output_batch_no: string | null;
};

type Scope = "active" | "cancelled" | "all";

type Props = { user: User };

export default function Production({ user }: Props) {
  const [orders, setOrders] = useState<Order[]>([]);
  const [materials, setMaterials] = useState<{ id: number; code: string; name: string; type: string }[]>([]);
  const [reservations, setReservations] = useState<Record<number, MaterialReservation[]>>({});
  const [scope, setScope] = useState<Scope>("active");
  const [productId, setProductId] = useState("");
  const [plannedQty, setPlannedQty] = useState("100");
  const [tTop, setTTop] = useState("108");
  const [tCa, setTCa] = useState("99.5");
  const [actualQty, setActualQty] = useState("80");
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const canProd = canWrite(user, "production");
  const canApprove = canWrite(user, "production-approve");

  const reload = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [orderRows, materialRows] = await Promise.all([getProductionOrders(), getMaterials()]);
      const reservationRows = await Promise.all(
        orderRows.map(async (order: Order) => [order.id, await getProductionReservations(order.id)] as const),
      );
      setOrders(sortByRef(orderRows, (row: Order) => row.order_no, (row: Order) => row.id));
      setMaterials(materialRows.filter((item: { type: string }) => item.type === "TP"));
      setReservations(Object.fromEntries(reservationRows));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không thể tải dữ liệu sản xuất.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void reload();
  }, [reload]);

  const visibleOrders = useMemo(() => {
    if (scope === "cancelled") return orders.filter((order) => order.status === "cancelled");
    if (scope === "all") return orders;
    return orders.filter((order) => order.status !== "cancelled");
  }, [orders, scope]);

  const summary = useMemo(() => {
    const cancelled = orders.filter((order) => order.status === "cancelled").length;
    const done = orders.filter((order) => order.status === "done").length;
    const running = orders.filter((order) => order.status !== "cancelled" && order.status !== "done").length;
    return { total: orders.length, running, cancelled, done };
  }, [orders]);

  async function runAction(action: () => Promise<unknown>, message: string) {
    setBusy(true);
    setError(null);
    setSuccess(null);
    try {
      await action();
      await reload();
      setSuccess(message);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không thể thực hiện thao tác.");
    } finally {
      setBusy(false);
    }
  }

  async function handleCreate(event: React.FormEvent) {
    event.preventDefault();
    await runAction(
      () => createProductionOrder({ product_material_id: Number(productId), planned_qty: Number(plannedQty) }),
      "Đã tạo mẻ sản xuất.",
    );
  }

  return (
    <div className="page-shell production-page">
      <PageHeader
        title="Quản lý sản xuất"
        description="Khi duyệt mẻ, hệ thống tự giữ chỗ nguyên liệu theo hạn dùng sớm nhất; khi bắt đầu mẻ sẽ xuất đúng các lô đã giữ chỗ."
      />

      <div className="ops-summary">
        <div className="ops-summary__item">
          <span>Tổng mẻ</span>
          <strong>{summary.total}</strong>
        </div>
        <div className="ops-summary__item">
          <span>Đang xử lý</span>
          <strong>{summary.running}</strong>
        </div>
        <div className={`ops-summary__item${summary.cancelled > 0 ? " ops-summary__item--warn" : ""}`}>
          <span>Đã hủy</span>
          <strong>{summary.cancelled}</strong>
        </div>
        <div className="ops-summary__item">
          <span>Hoàn thành</span>
          <strong>{summary.done}</strong>
        </div>
      </div>

      {!canProd && <AlertBanner tone="warning">{roleHint("production")}</AlertBanner>}
      {error && (
        <AlertBanner tone="danger" title="Không thể xử lý" onClose={() => setError(null)}>
          {error}
        </AlertBanner>
      )}
      {success && (
        <AlertBanner tone="success" title="Thành công" onClose={() => setSuccess(null)}>
          {success}
        </AlertBanner>
      )}

      {canProd && (
        <section className="card production-create">
          <header className="ops-form-head">
            <div>
              <h2>Tạo mẻ sản xuất mới</h2>
              <p>Chọn thành phẩm và số lượng kế hoạch — sau khi tạo, Quản lý nhà máy duyệt để giữ chỗ nguyên liệu.</p>
            </div>
          </header>

          <ol className="production-flow production-flow--row" aria-label="Quy trình mẻ sản xuất">
            <li>
              <strong>1. Tạo mẻ</strong>
              <span>Bản nháp kế hoạch</span>
            </li>
            <li>
              <strong>2. Duyệt & giữ chỗ</strong>
              <span>Hạn dùng sớm nhất</span>
            </li>
            <li>
              <strong>3. Bắt đầu SX</strong>
              <span>Xuất nguyên liệu</span>
            </li>
            <li>
              <strong>4. Điểm KS 2</strong>
              <span>Nhiệt độ & thành phần</span>
            </li>
            <li>
              <strong>5. Hoàn thành</strong>
              <span>Sản lượng thực tế</span>
            </li>
          </ol>

          <form className="form production-create__form" onSubmit={handleCreate}>
            <div className="form-grid production-create__grid">
              <label className="full">
                Sản phẩm
                <select value={productId} onChange={(event) => setProductId(event.target.value)} required>
                  <option value="">— Chọn sản phẩm —</option>
                  {materials.map((material) => (
                    <option key={material.id} value={material.id}>
                      {material.code} — {material.name}
                    </option>
                  ))}
                </select>
              </label>
              <label className="full">
                Số lượng kế hoạch (kg)
                <input
                  value={plannedQty}
                  onChange={(event) => setPlannedQty(event.target.value)}
                  type="number"
                  inputMode="decimal"
                  step="0.1"
                  min="0.1"
                  required
                />
              </label>
              <div className="full production-create__actions">
                <p className="production-create__hint">
                  Mẻ mới ở trạng thái bản nháp. Giữ chỗ nguyên liệu chỉ tạo sau khi Quản lý nhà máy duyệt.
                </p>
                <button type="submit" disabled={busy || !productId}>
                  {busy ? "Đang tạo…" : "Tạo mẻ sản xuất"}
                </button>
              </div>
            </div>
          </form>
        </section>
      )}

      <div className="page-tabs" role="tablist" aria-label="Lọc mẻ sản xuất">
        <button
          type="button"
          role="tab"
          className={scope === "active" ? "active" : undefined}
          aria-selected={scope === "active"}
          onClick={() => setScope("active")}
        >
          Đang xử lý
        </button>
        <button
          type="button"
          role="tab"
          className={scope === "cancelled" ? "active" : undefined}
          aria-selected={scope === "cancelled"}
          onClick={() => setScope("cancelled")}
        >
          Đã hủy{summary.cancelled > 0 ? ` (${summary.cancelled})` : ""}
        </button>
        <button
          type="button"
          role="tab"
          className={scope === "all" ? "active" : undefined}
          aria-selected={scope === "all"}
          onClick={() => setScope("all")}
        >
          Tất cả
        </button>
      </div>

      {loading && <p className="loading-state">Đang tải các mẻ sản xuất…</p>}
      {!loading && visibleOrders.length === 0 && (
        <EmptyState
          title={scope === "cancelled" ? "Không có mẻ đã hủy" : "Chưa có mẻ sản xuất"}
          description={
            scope === "cancelled"
              ? "Các mẻ hủy sẽ xuất hiện ở đây để tra cứu."
              : "Tạo mẻ mới để bắt đầu giữ chỗ nguyên liệu."
          }
        />
      )}
      {visibleOrders.map((order) => (
        <section className="card production-order-card" key={order.id}>
          <header className="ops-data-card__head production-order-card__head">
            <div>
              <h3>{shortRef(order.order_no)}</h3>
              <p className="production-order-card__product">{order.product_code}</p>
            </div>
            <StatusBadge status={order.status} />
          </header>

          <dl className="ops-data-card__grid production-order-card__grid">
            <div>
              <dt>Số lượng kế hoạch</dt>
              <dd>{Number(order.planned_qty).toLocaleString("vi-VN")} kg</dd>
            </div>
            <div>
              <dt>Lô thành phẩm</dt>
              <dd>{order.output_batch_no ? shortRef(order.output_batch_no) : "—"}</dd>
            </div>
          </dl>

          <div className="production-order-card__reservations">
            <h4>Phân bổ nguyên liệu</h4>
            {(reservations[order.id] ?? []).length === 0 ? (
              <p className="production-order-card__empty">
                {order.status === "cancelled"
                  ? "Mẻ đã hủy — không còn giữ chỗ nguyên liệu."
                  : order.status === "draft"
                    ? "Chưa giữ chỗ. Quản lý nhà máy duyệt mẻ sẽ tự phân bổ theo hạn dùng sớm nhất."
                    : "Chưa có giữ chỗ nguyên liệu cho mẻ này."}
              </p>
            ) : (
              <ul className="ops-card-list production-reservation-list">
                {reservations[order.id].map((item) => (
                  <li key={item.id} className="ops-mini-card">
                    <strong>{shortRef(item.batch_no)}</strong>
                    <span>
                      {item.quantity} kg — <StatusBadge status={item.status} />
                    </span>
                    <span>
                      {item.expiry_date
                        ? `HSD ${new Date(`${item.expiry_date}T00:00:00`).toLocaleDateString("vi-VN")}`
                        : "Không có HSD"}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {(order.status === "draft" && canApprove) ||
          (order.status === "approved" && canProd) ||
          (order.status !== "done" && order.status !== "cancelled") ? (
            <ActionBar align="start">
              {order.status === "draft" && canApprove && (
                <button
                  type="button"
                  className="secondary"
                  disabled={busy}
                  onClick={() =>
                    runAction(() => approveProductionOrder(order.id), "Đã duyệt và giữ chỗ nguyên liệu.")
                  }
                >
                  Duyệt và giữ chỗ nguyên liệu
                </button>
              )}
              {order.status === "approved" && canProd && (
                <button
                  type="button"
                  disabled={busy}
                  onClick={() =>
                    runAction(() => startProductionOrder(order.id, []), "Đã bắt đầu mẻ và xuất nguyên liệu.")
                  }
                >
                  Bắt đầu sản xuất
                </button>
              )}
              {order.status !== "done" && order.status !== "cancelled" && (
                <button
                  type="button"
                  className="secondary"
                  disabled={busy}
                  onClick={() => runAction(() => cancelProductionOrder(order.id), "Đã hủy mẻ và hoàn tồn giữ chỗ.")}
                >
                  Hủy mẻ
                </button>
              )}
            </ActionBar>
          ) : null}

          {order.status === "running" && canProd && (
            <section className="card production-run-panel" aria-label={`Điểm kiểm soát 2 và hoàn thành mẻ ${shortRef(order.order_no)}`}>
              <header className="ops-form-head">
                <div>
                  <h3>Điểm kiểm soát 2 và hoàn thành mẻ</h3>
                  <p>Nhập nhiệt độ đỉnh và hàm lượng thành phần chính, sau đó ghi nhận trước khi hoàn thành mẻ.</p>
                </div>
              </header>
              <div className="form-grid production-run-panel__grid">
                <label>
                  Nhiệt độ đỉnh (°C)
                  <input value={tTop} onChange={(event) => setTTop(event.target.value)} type="number" step="0.1" />
                </label>
                <label>
                  Hàm lượng thành phần chính (%)
                  <input value={tCa} onChange={(event) => setTCa(event.target.value)} type="number" step="0.01" />
                </label>
                <div className="full production-run-panel__actions">
                  <button
                    type="button"
                    className="secondary"
                    disabled={busy}
                    onClick={() =>
                      runAction(
                        () =>
                          addOperation(order.id, {
                            step_name: "chung_cat",
                            t_top: Number(tTop),
                            t_ca_percent: Number(tCa),
                          }),
                        "Đã ghi thông số vận hành và điểm kiểm soát 2.",
                      )
                    }
                  >
                    Ghi điểm kiểm soát 2
                  </button>
                </div>
                <label>
                  Sản lượng thực tế (kg)
                  <input
                    value={actualQty}
                    onChange={(event) => setActualQty(event.target.value)}
                    type="number"
                    step="0.1"
                  />
                </label>
                <div className="full production-run-panel__actions">
                  <button
                    type="button"
                    disabled={busy}
                    onClick={() =>
                      runAction(
                        () => completeProductionOrder(order.id, Number(actualQty)),
                        "Đã hoàn thành mẻ sản xuất.",
                      )
                    }
                  >
                    Hoàn thành mẻ
                  </button>
                </div>
              </div>
            </section>
          )}
        </section>
      ))}
    </div>
  );
}
