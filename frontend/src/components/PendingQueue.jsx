export default function PendingQueue({ pending, selectedId, onSelect }) {
  if (pending.length === 0) {
    return (
      <div className="queue-empty">
        <p>Queue is clear.</p>
        <p className="muted">Every recent RFQ was either auto-sent or already reviewed.</p>
      </div>
    );
  }

  return (
    <ul className="queue-list">
      {pending.map(({ request_id, result }) => {
        const score = result.risk?.score ?? 0;
        const level = score >= 0.7 ? "danger" : score >= 0.4 ? "warn" : "safe";
        return (
          <li
            key={request_id}
            className={`queue-item ${request_id === selectedId ? "is-selected" : ""}`}
            onClick={() => onSelect(request_id)}
          >
            <div className="queue-item-top">
              <span className="queue-customer">
                {result.parsed_rfq?.customer_name || "Unknown sender"}
              </span>
              <span className={`risk-chip risk-${level}`}>{score.toFixed(2)}</span>
            </div>
            <div className="queue-item-bottom">
              <span className="muted">${(result.quote_total_usd ?? 0).toFixed(2)}</span>
              {result.sanitizer?.is_suspicious && (
                <span className="flag-badge">flagged</span>
              )}
            </div>
          </li>
        );
      })}
    </ul>
  );
}