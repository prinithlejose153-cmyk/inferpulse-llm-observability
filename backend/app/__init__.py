from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.extensions import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)

    db.init_app(app)

    from app.models.conversation import Conversation
    from app.models.message import Message
    from app.models.inference_log import InferenceLog

    with app.app_context():
        db.create_all()

    @app.route("/")
    def home():
        return {
            "message": "InferPulse backend is running",
            "status": "ok"
        }

    from app.routes.conversation_routes import conversation_bp
    app.register_blueprint(conversation_bp)

    from app.routes.chat_routes import chat_bp
    app.register_blueprint(chat_bp)

    from app.routes.ingestion_routes import ingestion_bp
    app.register_blueprint(ingestion_bp)

    from app.routes.dashboard_routes import dashboard_bp
    app.register_blueprint(dashboard_bp)

    return app