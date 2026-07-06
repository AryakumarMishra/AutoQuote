import { useEffect, useState, useCallback } from "react";
import { getPending, getAuditLog, approve, getHealth } from "./api";
import PendingQueue from "./components/PendingQueue.jsx";
import QuoteDetail from "./components/QuoteDetail.jsx";
import AuditLog from "./components/AuditLog.jsx";

const POLL_INTERVAL_MS = 4000;

export default function App() {
  const [pending, setPending] = useState([]);
  const [auditEntries, setAuditEntries] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [mockMode, setMockMode] = useState(null);
  const [error, setError] = useState(null);

  const refresh = useCallback(async () => {
    try {
      const [pendingRes, auditRes] = await Promise.all([getPending(), getAuditLog()]);
      setPending(pendingRes);
      setAuditEntries(auditRes);
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  }, []);

  useEffect(() => {
    getHealth()
      .then((h) => setMockMode(h.mock_mode))
      .catch(() => setMockMode(null));

    refresh();
    const id = setInterval(refresh, POLL_INTERVAL_MS);
    return () => clearInterval(id);
  }, [refresh]);

  const handleDecision = async (requestId, approveDecision, notes) => {
    await approve(requestId, approveDecision, notes);
    if (selectedId === requestId) setSelectedId(null);
    await refresh();
  };

  const selectedEntry = pending.find((p) => p.request_id === selectedId) || null;

  return (
    <div className="app-shell">
      <header className="app-header">
        <h1>AutoQuote Sentinel</h1>
        <div className="header-right">
          {mockMode !== null && (
            <span className={`mode-badge ${mockMode ? "mode-mock" : "mode-live"}`}>
              {mockMode ? "mock mode" : "live"}
            </span>
          )}
          {error && <span className="error-badge">backend unreachable</span>}
        </div>
      </header>

      <main className="app-main">
        <aside className="app-sidebar">
          <h2 className="sidebar-title">Pending review ({pending.length})</h2>
          <PendingQueue pending={pending} selectedId={selectedId} onSelect={setSelectedId} />
        </aside>

        <section className="app-detail">
          <QuoteDetail entry={selectedEntry} onDecision={handleDecision} />
        </section>
      </main>

      <footer className="app-footer">
        <AuditLog entries={auditEntries} />
      </footer>
    </div>
  );
}