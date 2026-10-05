import { useEffect, useState } from "react";
import { Link, NavLink, useLocation } from "react-router-dom";
import type { User } from "./api";
import NotificationBell from "./components/NotificationBell";
import ThemeToggle from "./components/ThemeToggle";
import { nhan, VAI_TRO } from "./labels";

type Props = {
  user: User;
  onLogout: () => void;
  children: React.ReactNode;
};

export default function Layout({ user, onLogout, children }: Props) {
  const [menuOpen, setMenuOpen] = useState(false);
  const location = useLocation();
  const initial = (user.full_name || user.username || "?").trim().charAt(0).toLocaleUpperCase("vi");

  useEffect(() => {
    setMenuOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    if (!menuOpen) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") setMenuOpen(false);
    };
    window.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [menuOpen]);

  return (
    <div className={`layout${menuOpen ? " layout--menu-open" : ""}`}>
      {menuOpen ? (
        <button
          type="button"
          className="nav-overlay"
          aria-label="Đóng menu"
          onClick={() => setMenuOpen(false)}
        />
      ) : null}
      <aside
        id="app-sidebar"
        className={`sidebar${menuOpen ? " sidebar--open" : ""}`}
      >
        <div className="sidebar-brand">
          <div className="sidebar-brand__mark" aria-hidden="true">
            <span>OX</span>
          </div>
          <div className="sidebar-brand__text">
            <strong>Oxeyns</strong>
            <span>Quản trị chất lượng</span>
          </div>
        </div>
        <nav aria-label="Điều hướng chính">
          <NavLink to="/" end>
            Bảng tổng quan
          </NavLink>
          <NavLink to="/inventory">Tồn kho</NavLink>
          <NavLink to="/stock-in">Nhập kho</NavLink>
          <NavLink to="/stock-out">Xuất kho</NavLink>
          <NavLink to="/production">Sản xuất</NavLink>
          <NavLink to="/lab">Kiểm nghiệm</NavLink>
          <NavLink to="/quality">Phê duyệt chất lượng</NavLink>
          <NavLink to="/capa">Khắc phục sai lệch</NavLink>
          <NavLink to="/trace">Truy xuất lô</NavLink>
          <NavLink to="/purchase">Yêu cầu mua hàng</NavLink>
          <NavLink to="/haccp">Giám sát điểm kiểm soát</NavLink>
          <NavLink to="/audit">Nhật ký thao tác</NavLink>
          <NavLink to="/reports">Báo cáo và xuất file</NavLink>
          {user.role === "admin" ? <NavLink to="/users">Quản lý tài khoản</NavLink> : null}
        </nav>
        <Link to="/profile" className="sidebar-user" aria-label={`Hồ sơ: ${user.full_name}`}>
          <span className="sidebar-user__avatar" aria-hidden="true">
            {user.avatar_url ? <img src={user.avatar_url} alt="" /> : initial}
          </span>
          <div className="sidebar-user__meta">
            <strong>{user.full_name}</strong>
            {nhan(VAI_TRO, user.role) !== user.full_name ? (
              <span>{nhan(VAI_TRO, user.role)}</span>
            ) : null}
          </div>
        </Link>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <button
            type="button"
            className="topbar__menu"
            aria-label={menuOpen ? "Đóng menu" : "Mở menu"}
            aria-expanded={menuOpen}
            aria-controls="app-sidebar"
            onClick={() => setMenuOpen((open) => !open)}
          >
            {menuOpen ? "✕" : "☰"}
          </button>
          <strong
            className="topbar__title"
            title="Oxeyns — Quản trị chất lượng nhà máy"
            aria-label="Oxeyns — Quản trị chất lượng nhà máy"
          >
            <span className="topbar__title-full" aria-hidden="true">
              Oxeyns — Quản trị chất lượng nhà máy
            </span>
            <span className="topbar__title-short" aria-hidden="true">
              Oxeyns
            </span>
          </strong>
          <div className="topbar__actions">
            <NotificationBell />
            <ThemeToggle className="topbar__theme" />
            <span className="topbar__divider" aria-hidden="true" />
            <Link
              to="/profile"
              className="topbar-user"
              aria-label={`Hồ sơ: ${user.full_name} (${nhan(VAI_TRO, user.role)})`}
            >
              <span className="topbar-user__avatar" aria-hidden="true">
                {user.avatar_url ? <img src={user.avatar_url} alt="" /> : initial}
              </span>
              <span className="topbar-user__meta">
                <strong className="topbar-user__name">{user.full_name}</strong>
                <span className="topbar-user__role">
                  {nhan(VAI_TRO, user.role) === user.full_name
                    ? `@${user.username}`
                    : nhan(VAI_TRO, user.role)}
                </span>
              </span>
            </Link>
            <button
              type="button"
              className="topbar__logout"
              aria-label="Đăng xuất"
              onClick={onLogout}
            >
              <span className="topbar__logout-full">Đăng xuất</span>
              <span className="topbar__logout-short" aria-hidden="true">
                Thoát
              </span>
            </button>
          </div>
        </header>
        <main className="main">{children}</main>
      </div>
    </div>
  );
}
