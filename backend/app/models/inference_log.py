from datetime import datetime
from app.extensions import db
import uuid


class InferenceLog(db.Model):
    __tablename__ = "inference_logs"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    conversation_id = db.Column(db.String(36), nullable=True)

    provider = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(100), nullable=False)

    status = db.Column(db.String(50), nullable=False)
    error_message = db.Column(db.Text, nullable=True)

    latency_ms = db.Column(db.Integer, nullable=True)

    input_tokens = db.Column(db.Integer, default=0)
    output_tokens = db.Column(db.Integer, default=0)
    total_tokens = db.Column(db.Integer, default=0)

    input_preview = db.Column(db.Text, nullable=True)
    output_preview = db.Column(db.Text, nullable=True)

    request_started_at = db.Column(db.DateTime, nullable=True)
    request_completed_at = db.Column(db.DateTime, nullable=True)

    raw_payload = db.Column(db.JSON, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)