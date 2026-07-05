from app.config import settings
from app.qwen_client import call_qwen_json
from app.schemas import ParsedRFQ, SanitizerResult, RiskScore

_RISK_SYSTEM_PROMPT = """You score how risky it would be to auto-send a generated quote to a \
customer without human review. Consider: how many fields were ambiguous, whether any item \
lookup failed, and general plausibility of the request. You do NOT see the sanitizer's \
security finding -- that is applied separately and always wins if suspicious.

Respond with a JSON object only, in this exact shape:
{"score": 0.0-1.0, "reasons": ["short phrase", ...]}
"""


def _mock_score(parsed: ParsedRFQ) -> dict:
    score = 0.1 + 0.15 * len(parsed.ambiguous_fields)
    reasons = ["Mock scoring based on ambiguous field count."]
    if parsed.ambiguous_fields:
        reasons.append(f"{len(parsed.ambiguous_fields)} ambiguous field(s) in parsed RFQ.")
    return {"score": min(score, 1.0), "reasons": reasons}


def score_risk(
    parsed: ParsedRFQ,
    sanitizer: SanitizerResult,
    quote_total_usd: float,
) -> RiskScore:
    if settings.mock_mode or not settings.dashscope_api_key:
        result = _mock_score(parsed)
    else:
        user_prompt = (
            f"Ambiguous fields: {parsed.ambiguous_fields}\n"
            f"Number of line items: {len(parsed.items)}\n"
            f"Quote total (USD): {quote_total_usd}"
        )
        result = call_qwen_json(
            model=settings.model_risk,
            system_prompt=_RISK_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

    score = float(result.get("score", 1.0))
    reasons = list(result.get("reasons", []))

    # Sanitizer findings and the high-value threshold are hard overrides --
    # they are enforced here in code, not left to the model's discretion.
    if sanitizer.is_suspicious:
        score = max(score, 0.9)
        reasons.append("Sanitizer flagged this email as suspicious.")

    if quote_total_usd >= settings.high_value_threshold_usd:
        score = max(score, 0.7)
        reasons.append(f"Quote total ${quote_total_usd:.2f} meets/exceeds high-value threshold.")

    route = "human_review" if score >= 0.5 else "auto_send"
    if sanitizer.is_suspicious and score >= 0.9:
        route = "human_review"

    return RiskScore(score=round(score, 2), reasons=reasons, route=route)