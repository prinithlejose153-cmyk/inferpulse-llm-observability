from flask import Blueprint, jsonify
from app.models.inference_log import InferenceLog

dashboard_bp = Blueprint("dashboard_bp", __name__)


@dashboard_bp.route("/api/dashboard/recent-logs", methods=["GET"])
def recent_logs():
    logs = InferenceLog.query.order_by(InferenceLog.created_at.desc()).limit(20).all()

    return jsonify([
        serialize_log(log)
        for log in logs
    ])


@dashboard_bp.route("/api/dashboard/summary", methods=["GET"])
def dashboard_summary():
    logs = InferenceLog.query.all()

    total_requests = len(logs)
    success_count = len([log for log in logs if log.status == "success"])
    error_count = len([log for log in logs if log.status == "error"])

    total_tokens = sum(log.total_tokens or 0 for log in logs)

    latencies = [log.latency_ms for log in logs if log.latency_ms is not None]
    avg_latency = int(sum(latencies) / len(latencies)) if latencies else 0

    success_rate = round((success_count / total_requests) * 100, 2) if total_requests else 0

    providers = {}
    for log in logs:
        providers[log.provider] = providers.get(log.provider, 0) + 1

    return jsonify({
        "total_requests": total_requests,
        "success_count": success_count,
        "error_count": error_count,
        "success_rate": success_rate,
        "average_latency_ms": avg_latency,
        "total_tokens": total_tokens,
        "providers": providers
    })


def serialize_log(log):
    return {
        "id": log.id,
        "conversation_id": log.conversation_id,
        "provider": log.provider,
        "model": log.model,
        "status": log.status,
        "latency_ms": log.latency_ms,
        "input_tokens": log.input_tokens,
        "output_tokens": log.output_tokens,
        "total_tokens": log.total_tokens,
        "input_preview": log.input_preview,
        "output_preview": log.output_preview,
        "error_message": log.error_message,
        "created_at": log.created_at.isoformat()
    }