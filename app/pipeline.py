from app.sanitizer import sanitize
from app.parser import parse_rfq
from app.risk_scorer import score_risk
from app.mock_erp import lookup_price, check_stock
from app.schemas import PipelineResult


def run_pipeline(email_body: str) -> PipelineResult:
    # Stage 1: sanitize BEFORE anything else touches this text.
    sanitizer_result = sanitize(email_body)

    # Stage 2: parse into structured line items (parser still sees the
    # original text, wrapped in an untrusted-data delimiter -- see parser.py).
    parsed = parse_rfq(sanitizer_result.cleaned_text)

    # Stage 3: tool calls -- price + stock check against the mock ERP.
    quote_total = 0.0
    for item in parsed.items:
        lookup_key = item.sku or item.description
        priced = lookup_price(lookup_key)
        if priced is None:
            parsed.ambiguous_fields.append(f'No catalog match for "{lookup_key}"')
            continue

        item.sku = priced["sku"]
        item.unit_price_usd = priced["unit_price_usd"]
        item.line_total_usd = round(priced["unit_price_usd"] * item.quantity, 2)
        quote_total += item.line_total_usd

        if not check_stock(priced["sku"], item.quantity):
            parsed.ambiguous_fields.append(
                f'Insufficient stock for "{priced["sku"]}" (requested {item.quantity})'
            )

    quote_total = round(quote_total, 2)

    # Stage 4: risk scoring -- decides auto_send vs human_review, with
    # sanitizer findings and the high-value threshold enforced as hard
    # overrides inside score_risk() rather than left to model discretion.
    risk = score_risk(parsed, sanitizer_result, quote_total)

    if risk.route == "human_review":
        status = "pending_review"
    elif risk.route == "blocked":
        status = "blocked"
    else:
        status = "auto_sent"

    return PipelineResult(
        sanitizer=sanitizer_result,
        parsed_rfq=parsed,
        risk=risk,
        quote_total_usd=quote_total,
        status=status,
    )