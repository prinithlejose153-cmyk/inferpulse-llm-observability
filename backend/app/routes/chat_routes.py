from flask import Blueprint, request, jsonify
from datetime import datetime

from app.extensions import db
from app.models.conversation import Conversation
from app.models.message import Message
from app.services.llm_client import generate_gemini_reply
from app.sdk.inference_logger import InferenceLogger

chat_bp = Blueprint("chat_bp", __name__)


@chat_bp.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}

    user_message = data.get("message")
    conversation_id = data.get("conversation_id")

    if not user_message:
        return jsonify({"error": "message is required"}), 400

    if conversation_id:
        conversation = Conversation.query.get(conversation_id)
        if not conversation:
            return jsonify({"error": "conversation not found"}), 404
    else:
        conversation = Conversation(title=user_message[:50])
        db.session.add(conversation)
        db.session.commit()

    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=user_message
    )
    db.session.add(user_msg)
    db.session.commit()

    recent_messages = Message.query.filter_by(
        conversation_id=conversation.id
    ).order_by(Message.created_at.desc()).limit(8).all()

    recent_messages = list(reversed(recent_messages))

    context = [
        {
            "role": msg.role,
            "content": msg.content
        }
        for msg in recent_messages
    ]

    logger = InferenceLogger(
        provider="google",
        model="gemini-2.0-flash",
        ingestion_url="http://127.0.0.1:5000/api/ingest/inference-log"
    )

    try:
        assistant_reply = logger.run(
            conversation_id=conversation.id,
            messages=context,
            llm_function=generate_gemini_reply
        )
    except Exception as e:
        return jsonify({
            "error": "LLM call failed",
            "details": str(e)
        }), 500

    assistant_msg = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=assistant_reply
    )

    conversation.updated_at = datetime.utcnow()

    db.session.add(assistant_msg)
    db.session.commit()

    return jsonify({
        "conversation_id": conversation.id,
        "reply": assistant_reply
    })