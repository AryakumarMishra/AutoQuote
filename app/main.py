import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import IngestRequest, PipelineResult, ApprovalDecision
from app.pipeline import run_pipeline
from app.config import settings

app = FastAPI(title="AutoQuote Sentinel", version="0.1.0")

# Loosened for hackathon dev speed -- tighten before anything resembling
# production use.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for the demo. Swap for SQLite/Postgres before deployment
# if you need results to survive a restart.
_PENDING: dict[str, PipelineResult] = {}
_AUDIT_LOG: list[dict] = []


@app.get("/health")
def health():
    return {"status": "ok", "mock_mode": settings.mock_mode}


@app.post("/ingest", response_model=PipelineResult)
def ingest(req: IngestRequest):
    result = run_pipeline(req.email_body)

    request_id = str(uuid.uuid4())
    _AUDIT_LOG.append(
        {
            "request_id": request_id,
            "sender_email": req.sender_email,
            "status": result.status,
            "risk_score": result.risk.score if result.risk else None,
            "sanitizer_flagged": result.sanitizer.is_suspicious,
        }
    )

    if result.status == "pending_review":
        _PENDING[request_id] = result

    return result


@app.get("/pending")
def list_pending():
    return [{"request_id": rid, "result": res} for rid, res in _PENDING.items()]


@app.post("/approve")
def approve(decision: ApprovalDecision):
    if decision.request_id not in _PENDING:
        raise HTTPException(status_code=404, detail="No pending request with that id")

    result = _PENDING.pop(decision.request_id)
    outcome = "approved_sent" if decision.approve else "rejected"

    _AUDIT_LOG.append(
        {
            "request_id": decision.request_id,
            "reviewer_decision": outcome,
            "reviewer_notes": decision.reviewer_notes,
        }
    )

    return {"request_id": decision.request_id, "outcome": outcome, "quote": result}


@app.get("/audit-log")
def audit_log():
    return _AUDIT_LOG