import { useState } from "react";

export default function QuoteDetail({ entry, onDecision }) {
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (!entry) {
    return (
      <div className="detail-empty">
        <p>Select a quote from the queue to review it.</p>
      </div>
    );
  }

  const { request_id, result } = entry;
  const { sanitizer, parsed_rfq, risk, quote_total_usd } = result;

  const handleDecision = async (approveDecision) => {
    setSubmitting(true);
    try {
      await onDecision(request_id, approveDecision, notes);
      setNotes("");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="detail-panel">
      <header className="detail-header">
        <h2>{parsed_rfq?.customer_name || "Unknown sender"}</h2>
        <span className="detail-total">${(quote_total_usd ?? 0).toFixed(2)}</span>
      </header>

      {sanitizer?.is_suspicious && (
        <div className="alert-banner">
          <strong>Sanitizer flagged this request.</strong>
          <p>{sanitizer.reasoning}</p>
          {sanitizer.flagged_patterns?.length > 0 && (
            <ul>
              {sanitizer.flagged_patterns.map((p, i) => (
                <li key={i}>{p}</li>
              ))}
            </ul>
          )}
        </div>
      )}

      <section className="detail-section">
        <h3>Line items</h3>
        <table className="items-table">
          <thead>
            <tr>
              <th>SKU</th>
              <th>Description</th>
              <th>Qty</th>
              <th>Unit price</th>
              <th>Line total</th>
            </tr>
          </thead>
          <tbody>
            {parsed_rfq?.items?.map((item, i) => (
              <tr key={i}>
                <td>{item.sku || "—"}</td>
                <td>{item.description}</td>
                <td>{item.quantity}</td>
                <td>{item.unit_price_usd != null ? `$${item.unit_price_usd.toFixed(2)}` : "—"}</td>
                <td>{item.line_total_usd != null ? `$${item.line_total_usd.toFixed(2)}` : "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {parsed_rfq?.ambiguous_fields?.length > 0 && (
        <section className="detail-section">
          <h3>Ambiguous fields</h3>
          <ul className="ambiguous-list">
            {parsed_rfq.ambiguous_fields.map((f, i) => (
              <li key={i}>{f}</li>
            ))}
          </ul>
        </section>
      )}

      <section className="detail-section">
        <h3>Risk reasons</h3>
        <ul className="reasons-list">
          {risk?.reasons?.map((r, i) => (
            <li key={i}>{r}</li>
          ))}
        </ul>
      </section>

      <section className="detail-section">
        <label htmlFor="reviewer-notes">Reviewer notes (optional)</label>
        <textarea
          id="reviewer-notes"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows={2}
        />
      </section>

      <div className="detail-actions">
        <button
          className="btn btn-reject"
          disabled={submitting}
          onClick={() => handleDecision(false)}
        >
          Reject
        </button>
        <button
          className="btn btn-approve"
          disabled={submitting}
          onClick={() => handleDecision(true)}
        >
          Approve &amp; send
        </button>
      </div>
    </div>
  );
}