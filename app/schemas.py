from typing import List, Optional
from pydantic import BaseModel, Field


class LineItem(BaseModel):
    sku: Optional[str] = None
    description: str
    quantity: int
    unit: Optional[str] = None
    unit_price_usd: Optional[float] = None
    line_total_usd: Optional[float] = None


class ParsedRFQ(BaseModel):
    customer_name: Optional[str] = None
    items: List[LineItem] = Field(default_factory=list)
    notes: Optional[str] = None
    ambiguous_fields: List[str] = Field(default_factory=list)


class SanitizerResult(BaseModel):
    is_suspicious: bool
    flagged_patterns: List[str] = Field(default_factory=list)
    reasoning: Optional[str] = None
    cleaned_text: str


class RiskScore(BaseModel):
    score: float  # 0.0 (safe) - 1.0 (high risk)
    reasons: List[str] = Field(default_factory=list)
    route: str  # "auto_send" | "human_review" | "blocked"


class PipelineResult(BaseModel):
    sanitizer: SanitizerResult
    parsed_rfq: Optional[ParsedRFQ] = None
    risk: Optional[RiskScore] = None
    quote_total_usd: Optional[float] = None
    status: str  # "auto_sent" | "pending_review" | "blocked" | "error"


class IngestRequest(BaseModel):
    sender_email: str
    email_body: str


class ApprovalDecision(BaseModel):
    request_id: str
    approve: bool
    reviewer_notes: Optional[str] = None