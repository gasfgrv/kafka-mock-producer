import json


class AvroSchemaLoader:
    schema_path: str

    def __init__(self, schema_path: str):
        self.schema_path = schema_path

    def load(self) -> dict:
        with open(self.schema_path) as f:
            return json.load(f)
