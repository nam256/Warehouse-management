import { useCallback, useEffect, useState } from "react";
import {
  createUser,
  getUsers,
  updateUser,
  type AdminUser,
  type User,
} from "../api";
import AlertBanner from "../components/ui/AlertBanner";
import EmptyState from "../components/ui/EmptyState";
import PageHeader from "../components/ui/PageHeader";
import { nhan, VAI_TRO } from "../labels";

type Props = { user: User };

const ROLE_OPTIONS = Object.keys(VAI_TRO);

export default function Users({ user }: Props) {
  const [rows, setRows] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [msg, setMsg] = useState<string | null>(null);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState("thu_kho");

  const load = useCallback(async () => {
    setLoading(true);
    setErr(null);
    try {
      setRows(await getUsers());
    } catch (error) {
      setErr(error instanceof Error ? error.message : "Không thể tải danh sách tài khoản.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  if (user.role !== "admin") {
    return (
      <div className="page-shell users-page">
        <PageHeader title="Quản lý tài khoản" />
        <AlertBanner tone="warning">Chỉ quản trị viên mới được quản lý tài khoản.</AlertBanner>
      </div>
    );
  }

  async function onCreate(event: React.FormEvent) {
    event.preventDefault();
    setErr(null);
    setMsg(null);
    setBusy(true);
    try {
      await createUser({
        username: username.trim(),
        password,
        full_name: fullName.trim(),
        role,
      });
      setUsername("");
      setPassword("");
      setFullName("");
      setRole("thu_kho");
      setMsg("Đã tạo tài khoản mới.");
      await load();
    } catch (error) {
      setErr(error instanceof Error ? error.message : "Không thể tạo tài khoản.");
    } finally {
      setBusy(false);
    }
  }

  async function toggleActive(row: AdminUser) {
    setErr(null);
    setMsg(null);
    setBusy(true);
    try {
      await updateUser(row.id, { is_active: !row.is_active });
      setMsg(row.is_active ? `Đã khóa ${row.username}.` : `Đã mở lại ${row.username}.`);
      await load();
    } catch (error) {
      setErr(error instanceof Error ? error.message : "Không thể cập nhật tài khoản.");
    } finally {
      setBusy(false);
    }
  }

  async function changeRole(row: AdminUser, nextRole: string) {
    if (nextRole === row.role) return;
    setErr(null);
    setMsg(null);
    setBusy(true);
    try {
      await updateUser(row.id, { role: nextRole });
      setMsg(`Đã đổi vai trò ${row.username}.`);
      await load();
    } catch (error) {
      setErr(error instanceof Error ? error.message : "Không thể đổi vai trò.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="page-shell users-page">
      <PageHeader
        title="Quản lý tài khoản"
        description="Chỉ admin tạo tài khoản — không có đăng ký công khai."
      />

      {err && (
        <AlertBanner tone="danger" title="Lỗi" onClose={() => setErr(null)}>
          {err}
        </AlertBanner>
      )}
      {msg && (
        <AlertBanner tone="success" title="Thành công" onClose={() => setMsg(null)}>
          {msg}
        </AlertBanner>
      )}

      <div className="users-layout">
        <section className="card users-create">
          <h2>Tạo tài khoản</h2>
          <form className="form" onSubmit={(event) => void onCreate(event)}>
            <label>
              Tên đăng nhập
              <input
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                required
                minLength={3}
                autoComplete="off"
              />
            </label>
            <label>
              Mật khẩu tạm
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
                minLength={6}
                autoComplete="new-password"
              />
            </label>
            <label>
              Họ và tên
              <input
                value={fullName}
                onChange={(event) => setFullName(event.target.value)}
                required
              />
            </label>
            <label>
              Vai trò
              <select value={role} onChange={(event) => setRole(event.target.value)}>
                {ROLE_OPTIONS.map((key) => (
                  <option key={key} value={key}>
                    {nhan(VAI_TRO, key)}
                  </option>
                ))}
              </select>
            </label>
            <div className="form-actions">
              <button type="submit" disabled={busy}>
                {busy ? "Đang tạo…" : "Tạo tài khoản"}
              </button>
            </div>
          </form>
        </section>

        <section className="card users-list">
          <h2>Danh sách ({rows.length})</h2>
          {loading && <p className="loading-state">Đang tải…</p>}
          {!loading && rows.length === 0 && (
            <EmptyState title="Chưa có tài khoản" description="Tạo tài khoản đầu tiên ở form bên cạnh." />
          )}
          {!loading && rows.length > 0 && (
            <div className="users-table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Người dùng</th>
                    <th>Vai trò</th>
                    <th>Trạng thái</th>
                    <th>Thao tác</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row) => (
                    <tr key={row.id} className={row.is_active ? undefined : "users-row--inactive"}>
                      <td>
                        <strong>{row.full_name}</strong>
                        <div className="users-username">@{row.username}</div>
                      </td>
                      <td>
                        <select
                          value={row.role}
                          disabled={busy || row.id === user.id}
                          onChange={(event) => void changeRole(row, event.target.value)}
                          aria-label={`Vai trò ${row.username}`}
                        >
                          {ROLE_OPTIONS.map((key) => (
                            <option key={key} value={key}>
                              {nhan(VAI_TRO, key)}
                            </option>
                          ))}
                        </select>
                      </td>
                      <td>{row.is_active ? "Đang hoạt động" : "Đã khóa"}</td>
                      <td>
                        <button
                          type="button"
                          className="secondary"
                          disabled={busy || row.id === user.id}
                          onClick={() => void toggleActive(row)}
                        >
                          {row.is_active ? "Khóa" : "Mở khóa"}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
