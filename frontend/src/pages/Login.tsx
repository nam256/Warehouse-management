import { useState } from "react";
import ThemeToggle from "../components/ThemeToggle";
import { VAI_TRO, nhan } from "../labels";

type Props = { onLogin: (u: string, p: string) => Promise<void>; sessionExpired?: boolean };

const TAI_KHOAN_DEMO = [
  { user: "thu_kho", pass: "kho123", role: "thu_kho" },
  { user: "ky_thuat", pass: "kt123", role: "ky_thuat" },
  { user: "ql_nm", pass: "ql123", role: "ql_nm" },
  { user: "lab", pass: "lab123", role: "lab" },
  { user: "attp", pass: "attp123", role: "attp" },
  { user: "admin", pass: "admin123", role: "admin" },
];

export default function Login({ onLogin, sessionExpired }: Props) {
  const [username, setUsername] = useState("thu_kho");
  const [password, setPassword] = useState("kho123");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await onLogin(username, password);
    } catch {
      setError("Sai tên đăng nhập hoặc mật khẩu");
    } finally {
      setLoading(false);
    }
  }

  function chonTaiKhoan(user: string, pass: string) {
    setUsername(user);
    setPassword(pass);
    setError("");
  }

  return (
    <div className="login-page">
      <div className="login-page__glow" aria-hidden="true" />
      <ThemeToggle className="login-theme" />
      <div className="login-card">
        <div className="login-brand">
          <div className="login-logo" aria-hidden="true">
            <span>OX</span>
          </div>
          <div className="login-brand__text">
            <p className="login-brand__eyebrow">Digital QMS</p>
            <h1>Oxeyns Long An</h1>
            <p>Quản trị chất lượng nhà máy tinh dầu</p>
          </div>
        </div>

        <form className="login-form" onSubmit={submit}>
          {sessionExpired && (
            <p className="login-expired">Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.</p>
          )}
          <label>
            Tên đăng nhập
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Nhập tên đăng nhập"
              autoComplete="username"
            />
          </label>
          <label>
            Mật khẩu
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Nhập mật khẩu"
              autoComplete="current-password"
            />
          </label>
          {error && <p className="login-error">{error}</p>}
          <button type="submit" className="login-submit" disabled={loading}>
            {loading ? "Đang đăng nhập…" : "Đăng nhập"}
          </button>
        </form>

        <details className="login-demo" open>
          <summary>Tài khoản dùng thử</summary>
          <p className="login-demo__hint">Bấm một vai trò để điền sẵn form</p>
          <div className="login-demo-list">
            {TAI_KHOAN_DEMO.map((tk) => (
              <button
                key={tk.user}
                type="button"
                className={`login-demo-item${username === tk.user ? " active" : ""}`}
                onClick={() => chonTaiKhoan(tk.user, tk.pass)}
              >
                <span className="login-demo-role">{nhan(VAI_TRO, tk.role)}</span>
                <span className="login-demo-cred">
                  {tk.user} · {tk.pass}
                </span>
              </button>
            ))}
          </div>
        </details>
      </div>
    </div>
  );
}
