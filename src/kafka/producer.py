import json
import hashlib
from datetime import datetime
import platform
import re
import socket
from uuid import uuid4, getnode
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
        record_key = self.__generate_record_key(record)
        record_headers = self.__generate_record_headers()

        self.producer.produce(topic=topic, key=record_key,
                              value=record, headers=record_headers)
        self.producer.flush()

    @staticmethod
    def __generate_record_headers() -> dict:
        headers = {}
        headers['platform'] = platform.system()
        headers['platform-release'] = platform.release()
        headers['platform-version'] = platform.version()
        headers['architecture'] = platform.machine()
        headers['hostname'] = socket.gethostname()
        headers['ip-address'] = socket.gethostbyname(socket.gethostname())
        headers['mac-address'] = ':'.join(re.findall('..',
                                          '%012x' % getnode()))
        headers['processor'] = platform.processor()
        return headers

    @staticmethod
    def __generate_record_key(record: dict) -> str:
        hash_dict = record.copy()
        hash_dict.update(
            {"timestamp": datetime.now().isoformat(), "uuid": str(uuid4())})
        serialized_record = json.dumps(
            hash_dict, sort_keys=True).encode("utf-8")
        return hashlib.md5(serialized_record).hexdigest()
