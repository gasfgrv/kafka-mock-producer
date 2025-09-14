import json
import os

from confluent_kafka import KafkaException, SerializingProducer
from confluent_kafka.admin import AdminClient
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from fastavro import parse_schema, validate
from flask import Flask, request, jsonify

app = Flask(__name__)

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
SCHEMA_REGISTRY = os.getenv("SCHEMA_REGISTRY", "http://localhost:8081")
SCHEMA_PATH = os.getenv("SCHEMA_PATH", "./schemas/user.avsc")

with open(SCHEMA_PATH) as f:
    schema_dict = json.load(f)

parsed_schema = parse_schema(schema_dict)

schema_registry_conf = {"url": SCHEMA_REGISTRY}
schema_registry_client = SchemaRegistryClient(schema_registry_conf)

avro_serializer = AvroSerializer(
    schema_registry_client, json.dumps(schema_dict), to_dict=None)

producer_config = {
    "bootstrap.servers": KAFKA_BROKER,
    "value.serializer": avro_serializer
}

producer = SerializingProducer(producer_config)

admin_client = AdminClient({"bootstrap.servers": KAFKA_BROKER})


def topic_exists(topic):
    try:
        metadata = admin_client.list_topics(timeout=5)
        return topic in metadata.topics
    except KafkaException as e:
        print(f"Erro verificando tópico: {e}")
        return False


def validate_message(schema, message):
    try:
        return validate(message, schema)
    except Exception:
        return False


@app.route("/produce", methods=["POST"])
def produce_message():
    data = request.json
    topic = data.get("topic")
    message = data.get("message")

    if not topic or not message:
        return jsonify({"error": "Campos obrigatórios: topic, message"}), 400

    if not topic_exists(topic):
        return jsonify({"erros": f"Tópico '{topic}' não existe no Kafka"}), 404

    if not validate_message(parsed_schema, message):
        return jsonify({"error": "Mensagem não está em conformidade com o schema Avro"}), 400

    try:
        producer.produce(topic=topic, value=message)
        producer.flush()
        print(f"Enviado para o tópico {topic}: {message}")
        return jsonify({"status": "ok", "topic": topic, "message": message}), 200
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
