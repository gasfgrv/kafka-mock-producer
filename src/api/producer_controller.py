from logging import Logger

from flask import Blueprint, request, jsonify

from src.services.producer_service import ProducerService


def create_producer_blueprint(service: ProducerService, logger: Logger) -> Blueprint:
    producer_bp = Blueprint("producer", __name__)

    @producer_bp.route("/produce", methods=["POST"])
    def produce():
        data: dict = request.json or {}
        topic: str = data.get("topic")
        message: dict = data.get("message")

        if not topic or not message:
            logger.error(f"topic or message not provided: topic={topic}, message={message}")
            return jsonify({"error": "topic and message must be provided"}), 400

        try:
            service.produce(topic, message)
            return jsonify({"status": "ok", "topic": topic}), 200
        except ValueError as e:
            logger.error(str(e))
            return jsonify({"error": str(e)}), 400
        except Exception:
            logger.error("Internal server error", exc_info=True)
            return jsonify({"error": "Internal server error"}), 500

    return producer_bp
