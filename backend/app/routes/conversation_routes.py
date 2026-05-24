from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.conversation import Conversation
from app.models.message import Message

conversation_bp = Blueprint("conversation_bp", __name__)


@conversation_bp.route("/api/conversations", methods=["POST"])
def create_conversation():
    data = request.get_json() or {}

    conversation = Conversation(
        title=data.get("title", "New Conversation")
    )

    db.session.add(conversation)
    db.session.commit()

    return jsonify({
        "id": conversation.id,
        "title": conversation.title,
        "status": conversation.status,
        "created_at": conversation.created_at.isoformat()
    }), 201


@conversation_bp.route("/api/conversations", methods=["GET"])
def list_conversations():
    conversations = Conversation.query.order_by(Conversation.updated_at.desc()).all()

    return jsonify([
        {
            "id": c.id,
            "title": c.title,
            "status": c.status,
            "created_at": c.created_at.isoformat(),
            "updated_at": c.updated_at.isoformat()
        }
        for c in conversations
    ])


@conversation_bp.route("/api/conversations/<conversation_id>", methods=["GET"])
def get_conversation(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)

    messages = Message.query.filter_by(
        conversation_id=conversation.id
    ).order_by(Message.created_at.asc()).all()

    return jsonify({
        "id": conversation.id,
        "title": conversation.title,
        "status": conversation.status,
        "created_at": conversation.created_at.isoformat(),
        "updated_at": conversation.updated_at.isoformat(),
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "created_at": m.created_at.isoformat()
            }
            for m in messages
        ]
    })


@conversation_bp.route("/api/conversations/<conversation_id>", methods=["DELETE"])
def delete_conversation(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)

    db.session.delete(conversation)
    db.session.commit()

    return jsonify({
        "message": "Conversation deleted successfully"
    })