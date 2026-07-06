export default function AuditLog({ entries }) {
  return (
    <div className="audit-log">
      <div className="audit-log-header">audit log — live</div>
      <div className="audit-log-body">
        {entries.length === 0 && <div className="audit-line muted">// no events yet</div>}
        {entries
          .slice()
          .reverse()
          .map((entry, i) => (
            <div className="audit-line" key={i}>
              <span className="audit-ts">#{entry.request_id?.slice(0, 8) ?? "system"}</span>{" "}
              {entry.status && <span>status={entry.status}</span>}
              {entry.risk_score != null && <span> risk={entry.risk_score}</span>}
              {entry.sanitizer_flagged && <span className="audit-flag"> flagged</span>}
              {entry.reviewer_decision && (
                <span> decision={entry.reviewer_decision}</span>
              )}
              {entry.reviewer_notes && <span> notes="{entry.reviewer_notes}"</span>}
            </div>
          ))}
      </div>
    </div>
  );
}