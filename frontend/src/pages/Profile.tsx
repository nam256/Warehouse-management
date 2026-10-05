import { useRef, useState } from "react";
import {
  changePassword,
  updateMe,
  uploadAvatar,
  type User,
} from "../api";
import AlertBanner from "../components/ui/AlertBanner";
import PageHeader from "../components/ui/PageHeader";
import { nhan, VAI_TRO } from "../labels";

type Props = {
  user: User;
  onUserChange: (user: User) => void;
};

export default function Profile({ user, onUserChange }: Props) {
  const [fullName, setFullName] = useState(user.full_name);
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [busy, setBusy] = useState<"profile" | "password" | "avatar" | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [msg, setMsg] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  async function saveProfile(event: React.FormEvent) {
    event.preventDefault();
    setErr(null);
    setMsg(null);
    const name = fullName.trim();
    if (!name) {
      setErr("Họ tên không được để trống.");
      return;
    }
    setBusy("profile");
    try {
      const updated = await updateMe({ full_name: name });
      onUserChange(updated);
      setMsg("Đã cập nhật hồ sơ.");
    } catch (error) {
      setErr(error instanceof Error ? error.message : "Không thể cập nhật hồ sơ.");
    } finally {
      setBusy(null);
    }
  }

  async function savePassword(event: React.FormEvent) {
    event.preventDefault();
    setErr(null);
    setMsg(null);
    if (newPassword.length < 6) {
      setErr("Mật khẩu mới phải có ít nhất 6 ký tự.");
      return;
    }
    if (newPassword !== confirmPassword) {
      setErr("Xác nhận mật khẩu không khớp.");
      return;
    }
    setBusy("password");
    try {
      await changePassword(currentPassword, newPassword);
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setMsg("Đã đổi mật khẩu. Lần sau đăng nhập bằng mật khẩu mới.");
    } catch (error) {
      setErr(error instanceof Error ? error.message : "Không thể đổi mật khẩu.");
    } finally {
      setBusy(null);
    }
  }

  async function onAvatarSelected(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    setErr(null);
    setMsg(null);
    setBusy("avatar");
    try {
      const updated = await uploadAvatar(file);
      onUserChange(updated);
      setMsg("Đã cập nhật ảnh đại diện.");
    } catch (error) {
      setErr(error instanceof Error ? error.message : "Không thể tải ảnh đại diện.");
    } finally {
      setBusy(null);
    }
  }

  const initial = (user.full_name || user.username || "?").trim().charAt(0).toLocaleUpperCase("vi");

  return (
    <div className="page-shell profile-page">
      <PageHeader
        title="Hồ sơ của tôi"
        description="Xem thông tin tài khoản, đổi họ tên và mật khẩu."
      />

      {err && (
        <AlertBanner tone="danger" title="Không thể lưu" onClose={() => setErr(null)}>
          {err}
        </AlertBanner>
      )}
      {msg && (
        <AlertBanner tone="success" title="Thành công" onClose={() => setMsg(null)}>
          {msg}
        </AlertBanner>
      )}

      <div className="profile-layout">
        <section className="card profile-card">
          <div className="profile-identity">
            <button
              type="button"
              className="profile-avatar"
              onClick={() => fileRef.current?.click()}
              disabled={busy === "avatar"}
              aria-label="Đổi ảnh đại diện"
            >
              {user.avatar_url ? (
                <img src={user.avatar_url} alt="" />
              ) : (
                <span aria-hidden="true">{initial}</span>
              )}
            </button>
            <input
              ref={fileRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              hidden
              onChange={(event) => void onAvatarSelected(event)}
            />
            <div>
              <strong>{user.full_name}</strong>
              <p>
                @{user.username} · {nhan(VAI_TRO, user.role)}
              </p>
              <button
                type="button"
                className="secondary"
                disabled={!!busy}
                onClick={() => fileRef.current?.click()}
              >
                {busy === "avatar" ? "Đang tải…" : "Đổi ảnh đại diện"}
              </button>
            </div>
          </div>

          <form className="form" onSubmit={(event) => void saveProfile(event)}>
            <label>
              Họ và tên
              <input
                value={fullName}
                onChange={(event) => setFullName(event.target.value)}
                required
                autoComplete="name"
              />
            </label>
            <label>
              Tên đăng nhập
              <input value={user.username} disabled readOnly />
            </label>
            <label>
              Vai trò
              <input value={nhan(VAI_TRO, user.role)} disabled readOnly />
            </label>
            <div className="form-actions">
              <button type="submit" disabled={busy === "profile"}>
                {busy === "profile" ? "Đang lưu…" : "Lưu hồ sơ"}
              </button>
            </div>
          </form>
        </section>

        <section className="card profile-card">
          <h2>Đổi mật khẩu</h2>
          <form className="form" onSubmit={(event) => void savePassword(event)}>
            <label>
              Mật khẩu hiện tại
              <input
                type="password"
                value={currentPassword}
                onChange={(event) => setCurrentPassword(event.target.value)}
                required
                autoComplete="current-password"
              />
            </label>
            <label>
              Mật khẩu mới
              <input
                type="password"
                value={newPassword}
                onChange={(event) => setNewPassword(event.target.value)}
                required
                minLength={6}
                autoComplete="new-password"
              />
            </label>
            <label>
              Xác nhận mật khẩu mới
              <input
                type="password"
                value={confirmPassword}
                onChange={(event) => setConfirmPassword(event.target.value)}
                required
                minLength={6}
                autoComplete="new-password"
              />
            </label>
            <div className="form-actions">
              <button type="submit" disabled={busy === "password"}>
                {busy === "password" ? "Đang đổi…" : "Đổi mật khẩu"}
              </button>
            </div>
          </form>
        </section>
      </div>
    </div>
  );
}
