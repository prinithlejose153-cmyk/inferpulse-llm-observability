from flask import Blueprint, request, jsonify
from datetime import datetime

from app.extensions import db
from app.models.inference_log import InferenceLog
from app.services.redaction import redact_pii

ingestion_bp = Blueprint("ingestion_bp", __name__)


@ingestion_bp.route("/api/ingest/inference-log", methods=["POST"])
def ingest_inference_log():
    payload = request.get_json() or {}

    required_fields = ["provider", "model", "status", "conversation_id"]

    missing = [field for field in required_fields if field not in payload]
    if missing:
        return jsonify({
            "error": "Invalid payload",
            "missing_fields": missing
        }), 400

    input_preview = redact_pii(payload.get("input_preview"))
    output_preview = redact_pii(payload.get("output_preview"))
    error_message = redact_pii(payload.get("error_message"))

    log = InferenceLog(
        conversation_id=payload.get("conversation_id"),
        provider=payload.get("provider"),
        model=payload.get("model"),
        status=payload.get("status"),
        error_message=error_message,
        latency_ms=payload.get("latency_ms"),
        input_tokens=payload.get("input_tokens", 0),
        output_tokens=payload.get("output_tokens", 0),
        total_tokens=payload.get("total_tokens", 0),
        input_preview=input_preview,
        output_preview=output_preview,
        request_started_at=parse_datetime(payload.get("request_started_at")),
        request_completed_at=parse_datetime(payload.get("request_completed_at")),
        raw_payload=payload
    )

    db.session.add(log)
    db.session.commit()

    return jsonify({
        "message": "Inference log ingested successfully",
        "log_id": log.id
    }), 201


@ingestion_bp.route("/api/ingest/health", methods=["GET"])
def ingestion_health():
    return jsonify({
        "status": "ok",
        "service": "ingestion"
    })


def parse_datetime(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None