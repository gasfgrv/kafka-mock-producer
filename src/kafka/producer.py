import json
import hashlib
from datetime import datetime
from uuid import uuid4
from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer


class KafkaProducerService:
    producer: SerializingProducer
    avro_serializer: AvroSerializer

    def __init__(self, broker: str, schema_registry_url: str, schema: dict):
        self.avro_serializer = AvroSerializer(
            schema_registry_client=SchemaRegistryClient(
                {"url": schema_registry_url}),
            schema_str=json.dumps(schema),
            to_dict=None
        )
        self.producer = SerializingProducer({
            "bootstrap.servers": broker,
            "value.serializer": self.avro_serializer
        })

    def send(self, topic: str, record: dict):
        hash_dict = record.copy()
        hash_dict.update(
            {"timestamp": datetime.now().isoformat(), "uuid": str(uuid4())})
        serialized_record = json.dumps(
            hash_dict, sort_keys=True).encode("utf-8")
        record_key = hashlib.md5(serialized_record).hexdigest()

        self.producer.produce(topic=topic, key=record_key, value=record)
        self.producer.flush()
