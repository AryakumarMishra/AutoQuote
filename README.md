# AutoQuote

An Autopilot Agent (Track 4; Qwen Devpost Hackathon) that turns inbound B2B RFQ emails into quotes —
with a dedicated sanitizer layer that defends against prompt injection
embedded in untrusted inbound email, and a risk-scored human-in-the-loop
gate before anything gets sent to a customer.

## Pipeline

`sanitize -> parse (Qwen) -> price/stock lookup (mock ERP) -> risk score (Qwen) -> route`

Two hard overrides are enforced in code (not left to model discretion):
- Sanitizer flags the input as suspicious -> forced to human review
- Quote total exceeds `HIGH_VALUE_THRESHOLD_USD` -> forced to human review

## Setup

```bash
cd autoquote-sentinel
pip install -r requirements.txt
cp .env.example .env
```

The `MOCK_MODE=true` is for while building -- every Qwen call is replaced with a
deterministic mock, so you can develop and test the whole pipeline without
spending API credits.

Run the server:

```bash
uvicorn app.main:app --reload --port 8000
```

## Endpoints

- `GET /health` -- liveness + confirms mock mode status
- `POST /ingest` -- body: `{"sender_email": str, "email_body": str}`, runs the full pipeline
- `GET /pending` -- quotes currently sitting in human review
- `POST /approve` -- body: `{"request_id": str, "approve": bool, "reviewer_notes": str}`
- `GET /audit-log` -- full decision trail (every sanitizer/risk outcome, every human override)