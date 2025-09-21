import json
import logging
import os
import sys

from confluent_kafka import KafkaException, SerializingProducer
from confluent_kafka.admin import AdminClient
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from fastavro import parse_schema, validate
from flask import Flask, request, jsonify
from pythonjsonlogger import json as jsonlogger

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
SCHEMA_REGISTRY = os.getenv("SCHEMA_REGISTRY", "http://localhost:8081")
SCHEMA_PATH = os.getenv("SCHEMA_PATH", "./schemas/user.avsc")


def _config_logger():
    logging_config = logging.getLogger("mock-producer")
    logging_config.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)

    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s",
        json_ensure_ascii=False)
    stream_handler.setFormatter(formatter)

    logging_config.addHandler(stream_handler)
    return logging_config


app = Flask(__name__)

logger = _config_logger()
app.logger = logger


def _get_avro():
    with open(SCHEMA_PATH) as f:
        schema_dict = json.load(f)
        return schema_dict


def _topic_exists(topic):
    try:
        logger.info(msg=f"Verificando existência do tópico '{topic}'")
        admin_client = AdminClient(conf={"bootstrap.servers": KAFKA_BROKER})
        metadata = admin_client.list_topics(timeout=5)
        return topic in metadata.topics
    except KafkaException as e:
        logger.error(msg=f"Erro verificando tópico: {e}")
        return False


def _validate_message(schema, message):
    try:
        logger.info(msg="Validando mensagem contra o schema Avro")
        return validate(message, schema)
    except Exception as e:
        logger.error(msg=f"Erro validando mensagem: {e}")
        return False


@app.route("/produce", methods=["POST"])
def produce_message():
    data = request.json
    topic = data.get("topic")
    message = data.get("message")

    schema = _get_avro()
    parsed_schema = parse_schema(schema)

    if not topic or not message:
        logger.error(msg="Campos obrigatórios ausentes")
        return jsonify({"error": "Campos obrigatórios: topic, message"}), 400

    if not _topic_exists(topic):
        logger.error(msg=f"Tópico '{topic}' não existe")
        return jsonify({"erros": f"Tópico '{topic}' não existe no Kafka"}), 404

    if not _validate_message(parsed_schema, message):
        logger.error(msg="Mensagem não está em conformidade com o schema Avro")
        return jsonify({"error": "Mensagem não está em conformidade com o schema Avro"}), 400

    try:
        logger.info(msg=f"Enviando mensagem para o tópico '{topic}': {message}")

        avro_serializer = AvroSerializer(
            schema_registry_client=SchemaRegistryClient(
                conf={"url": SCHEMA_REGISTRY}),
            schema_str=json.dumps(schema),
            to_dict=None
        )

        producer = SerializingProducer(conf={
            "bootstrap.servers": KAFKA_BROKER,
            "value.serializer": avro_serializer
        })
        producer.produce(topic=topic, value=message)
        producer.flush()

        logger.info(msg=f"Mensagem enviada para o tópico '{topic}'")
        return jsonify({"status": "ok", "topic": topic, "message": message}), 200
    except Exception as e:
        logger.error(msg=f"Erro ao enviar mensagem para o Kafka: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
