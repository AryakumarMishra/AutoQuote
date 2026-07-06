const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${detail}`);
  }
  return res.json();
}

export function getHealth() {
  return request("/health");
}

export function getPending() {
  return request("/pending");
}

export function getAuditLog() {
  return request("/audit-log");
}

export function approve(requestId, approveDecision, reviewerNotes) {
  return request("/approve", {
    method: "POST",
    body: JSON.stringify({
      request_id: requestId,
      approve: approveDecision,
      reviewer_notes: reviewerNotes || null,
    }),
  });
}