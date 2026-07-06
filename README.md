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


## Going from mock to live Qwen Cloud
 
1. Fill in `DASHSCOPE_API_KEY` in `.env`
2. Verify the exact model IDs in the Qwen Cloud / Model Studio dashboard --
   `qwen-turbo` / `qwen-plus` in `.env.example` are a reasonable starting
   point but confirm against current docs before the deadline.
3. Set `MOCK_MODE=false`.
4. Re-run the two test cases from development (a normal RFQ and an
   injection-attempt RFQ) and confirm routing still works as expected --
   this is your demo video's core "wow" moment.
## Frontend (HITL approval dashboard)
 
```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```
 
Opens on `http://localhost:5173`. It polls the backend's `/pending` and
`/audit-log` endpoints every 4 seconds and posts to `/approve` when you
click Approve/Reject. Run the backend (`uvicorn app.main:app --reload`)
first, or the dashboard will show a "backend unreachable" badge.
 
## Still to build
 
- [x] React HITL dashboard (calls `/pending` and `/approve`)
- [ ] Real email ingestion (webhook or IMAP poll) feeding `/ingest`
- [ ] Swap in-memory `_PENDING` / `_AUDIT_LOG` for SQLite so state survives a restart
- [ ] Deploy to Alibaba Cloud ECS free-trial instance; record the proof-of-deployment clip
- [ ] Architecture diagram + demo video + writeup for submission