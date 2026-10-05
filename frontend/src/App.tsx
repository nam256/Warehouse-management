import { Navigate, Route, Routes, useLocation, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { getMe, login, type User } from "./api";
import { clearStoredToken, isStoredTokenValid, saveStoredToken } from "./auth";
import Layout from "./Layout";
import Dashboard from "./pages/Dashboard";
import Inventory from "./pages/Inventory";
import StockIn from "./pages/StockIn";
import StockOut from "./pages/StockOut";
import Production from "./pages/Production";
import Lab from "./pages/Lab";
import Trace from "./pages/Trace";
import PurchaseRequests from "./pages/PurchaseRequests";
import Audit from "./pages/Audit";
import Haccp from "./pages/Haccp";
import Reports from "./pages/Reports";
import Login from "./pages/Login";
import QualityRelease from "./pages/QualityRelease";
import Capa from "./pages/Capa";
import Profile from "./pages/Profile";
import Users from "./pages/Users";
import { ErrorBoundary } from "./components/ui/ErrorBoundary";
import AssistantWidget from "./components/AssistantWidget";
import { clearAssistantThread } from "./assistantThread";

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [sessionExpired, setSessionExpired] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (!isStoredTokenValid()) {
      clearStoredToken();
      setLoading(false);
      return;
    }
    getMe()
      .then(setUser)
      .catch(() => clearStoredToken())
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    function onExpired() {
      setUser(null);
      setSessionExpired(true);
      navigate("/login", { replace: true });
    }
    window.addEventListener("auth:expired", onExpired);
    return () => window.removeEventListener("auth:expired", onExpired);
  }, [navigate]);

  async function handleLogin(username: string, password: string) {
    const { access_token } = await login(username, password);
    saveStoredToken(access_token);
    const me = await getMe();
    setUser(me);
    setSessionExpired(false);
    navigate("/");
  }

  function logout() {
    if (user) clearAssistantThread(user.username);
    clearStoredToken();
    setUser(null);
    setSessionExpired(false);
    navigate("/login");
  }

  if (loading) return <p style={{ padding: "2rem" }}>Đang tải...</p>;

  if (!user) {
    return (
      <ErrorBoundary key={location.pathname}>
        <Routes>
          <Route
            path="/login"
            element={<Login onLogin={handleLogin} sessionExpired={sessionExpired || Boolean(location.state?.expired)} />}
          />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </ErrorBoundary>
    );
  }

  return (
    <Layout user={user} onLogout={logout}>
      <ErrorBoundary key={location.pathname}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/inventory" element={<Inventory user={user} />} />
          <Route path="/stock-in" element={<StockIn />} />
          <Route path="/stock-out" element={<StockOut user={user} />} />
          <Route path="/production" element={<Production user={user} />} />
          <Route path="/lab" element={<Lab user={user} />} />
          <Route path="/quality" element={<QualityRelease user={user} />} />
          <Route path="/capa" element={<Capa user={user} />} />
          <Route path="/trace" element={<Trace user={user} />} />
          <Route path="/purchase" element={<PurchaseRequests />} />
          <Route path="/audit" element={<Audit user={user} />} />
          <Route path="/haccp" element={<Haccp />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/profile" element={<Profile user={user} onUserChange={setUser} />} />
          <Route path="/users" element={<Users user={user} />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </ErrorBoundary>
      <AssistantWidget username={user.username} />
    </Layout>
  );
}
