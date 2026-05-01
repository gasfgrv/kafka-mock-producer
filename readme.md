# Kafka Avro Producer com Flask

Este projeto implementa um **producer Kafka** que envia mensagens em formato **Avro** usando um schema definido em
arquivo `.avsc`. A aplicação expõe uma API REST com **Flask** para enviar mensagens a tópicos Kafka, validando as
mensagens contra o schema.

O ambiente de execução é orquestrado com **Docker Compose**, incluindo Kafka, Zookeeper, Schema Registry e Kafka UI.

---

## Tecnologias utilizadas

- Python 3.x
- Flask
- Confluent Kafka Python Client (`confluent_kafka`)
- Fastavro
- Docker & Docker Compose
- Kafka
- Schema Registry
- Pytest (testes unitários)
- Freezegun (testes com tempo congelado)

---

## Estrutura do projeto

```
├── app.py # Script principal da API Flask
├── schemas/
│ └── user.avsc # Schema Avro para validação das mensagens
├── docker-compose.yml # Compose para Kafka, Zookeeper, Schema Registry e Kafka UI
└── README.md
```

---

## Configuração do Kafka e Schema Registry

O projeto usa **Docker Compose** para levantar o ambiente completo:

- **Zookeeper**: necessário para Kafka.
- **Kafka**: broker que receberá as mensagens.
- **Schema Registry**: gerencia os schemas Avro.
- **Kafka UI**: interface web para visualizar tópicos e mensagens.

### Rodando o ambiente

```bash
docker-compose up -d
```

Verifique os serviços:

* Kafka UI: http://localhost:8080
* Schema Registry: http://localhost:8081

---

## Configuração do Python

| Variável          | Padrão                  | Descrição                  |
|-------------------|-------------------------|----------------------------|
| `KAFKA_BROKER`    | `localhost:9092`        | Endpoint do broker Kafka   |
| `SCHEMA_REGISTRY` | `http://localhost:8081` | URL do Schema Registry     |
| `SCHEMA_PATH`     | `./schemas/user.avsc`   | Caminho para o schema Avro |

---

## Testes Unitários

O projeto utiliza **Pytest** para testes unitários e **Freezegun** para congelar o tempo durante os testes, garantindo que todos os testes sejam executados com um timestamp determinístico de `2024-01-01T00:00:00`.

### Executar os testes

```bash
# Instalar as dependências de teste
pip install -r requirements.txt

# Executar todos os testes
pytest

# Executar testes com verbose
pytest -v

# Executar um arquivo de teste específico
pytest tests/test_producer.py

# Executar com cobertura de código
pytest -cov=src tests/
```

### Por que usar Freezegun?

O **Freezegun** congela o tempo em um ponto específico, permitindo que:
- Testes relacionados a timestamps sejam **determinísticos** e **reproduzíveis**
- A chave de hash das mensagens seja sempre a mesma
- Não haja variações nos testes devido a diferenças de tempo de execução

### Exemplos de testes

- **test_producer.py**: Valida a inicialização do `KafkaProducerService` e a serialização de mensagens com timestamp congelado
- **test_schema_registry.py**: Testa integração com Schema Registry
- **test_avro_validator.py**: Valida conformidade com schemas Avro
- **test_producer_service.py**: Testa a lógica de negócio do serviço
- **test_producer_controller.py**: Testa endpoints da API Flask

---

## Debug no VS Code

Para executar o projeto no VS Code usando o ambiente virtual do projeto, adicione o seguinte arquivo em `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Flask (app)",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/main.py",
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}",
      "env": {
        "FLASK_APP": "main.py",
        "FLASK_ENV": "development"
      },
      "args": ["run", "--debug", "--host=0.0.0.0", "--port=5000"],
      "justMyCode": true,
      "python": "${workspaceFolder}/.venv/bin/python"
    }
  ]
}
```

Com essa configuração, o VS Code usará o interpretador Python do `.venv` e iniciará a aplicação Flask no projeto.

---

## Headers das mensagens

Cada mensagem enviada inclui automaticamente headers com informações do sistema que as enviou. Os headers incluem:

| Header             | Descrição                                 |
|-------------------|-------------------------------------------|
| `platform`        | Sistema operacional (Linux, Windows, etc) |
| `platform-release`| Versão do SO                              |
| `platform-version`| Detalhes completos da versão do SO        |
| `architecture`    | Arquitetura do processador (x86_64, arm64, etc) |
| `hostname`        | Nome do host que enviou a mensagem        |
| `ip-address`      | Endereço IP do host                       |
| `mac-address`     | Endereço MAC do host                      |
| `processor`       | Tipo/modelo do processador                |

### Exemplo de mensagem com headers

Quando uma mensagem é enviada, ela contém:

```json
{
  "topic": "users",
  "key": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "value": {
    "id": "123",
    "name": "João Silva"
  },
  "headers": {
    "platform": "Linux",
    "platform-release": "5.10.0-13-generic",
    "platform-version": "#1-Ubuntu SMP",
    "architecture": "x86_64",
    "hostname": "ubuntu-server",
    "ip-address": "192.168.1.100",
    "mac-address": "00:1a:2b:3c:4d:5e",
    "processor": "Intel(R) Core(TM) i7-9700K CPU"
  }
}
```

---

## Schema Avro de exemplo

O schema definido em `schemas/user.avsc`:

```json
{
  "type": "record",
  "namespace": "com.exemplo",
  "name": "User",
  "fields": [
    {
      "name": "id",
      "type": "string"
    },
    {
      "name": "name",
      "type": "string"
    },
    {
      "name": "age",
      "type": "int"
    }
  ]
}

```

Todas as mensagens enviadas devem estar em conformidade com este schema.

---

## Endpoints da API

### `POST /produce`

Envia uma mensagem para um tópico Kafka.

[![Run in Insomnia}](https://insomnia.rest/images/run.svg)](https://insomnia.rest/run/?label=kafka-mock-producer&uri=https%3A%2F%2Fraw.githubusercontent.com%2Fgasfgrv%2Fkafka-mock-producer%2Frefs%2Fheads%2Fmaster%2FInsomnia.yaml)

**Request Body:**

```json
{
  "topic": "nome_do_topico",
  "message": {
    "id": "123",
    "name": "João",
    "age": 30
  }
}
```

**Respostas possíveis:**

* **200 OK:** mensagem enviada com sucesso

```json
{
  "status": "ok",
  "topic": "nome_do_topico",
  "message": {
    "id": "123",
    "name": "João",
    "age": 30
  }
}
```

* **400 Bad Request:** campos obrigatórios faltando ou mensagem inválida

```json
{
  "error": "Campos obrigatórios: topic, message"
}
```

* **404 Not Found:** tópico não existe

```json
{
  "erros": "Tópico 'teste' não existe no Kafka"
}
```

* **500 Internal Server Error:** erro ao enviar a mensagem

---

## Funcionalidades principais do script

1. Validação de tópico Kafka:
    * Verifica se o tópico informado existe antes de enviar a mensagem.
2. Validação de mensagem Avro:
    * Usa fastavro para validar se a mensagem segue o schema definido.
3. Envio de mensagens:
    * Produz mensagens serializadas em Avro para o Kafka usando SerializingProducer.
4. Logs e erros:
    * Imprime no console mensagens enviadas e erros encontrados.

--- 

## Exemplo de uso

Criar um tópico no Kafka (via Kafka UI ou CLI):

```shell
kafka-topics --create --topic user-topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

Enviar uma mensagem via `curl`:

```shell
curl -X POST http://localhost:5000/produce \
  -H "Content-Type: application/json" \
  -d '{
        "topic": "user-topic",
        "message": { "id": "1", "name": "Alice", "age": 25 }
      }'
```

---

## Observações

* O `SerializingProducer` do Confluent Kafka cuida da serialização Avro ao enviar mensagens.
* É necessário que o schema esteja registrado no Schema Registry antes do envio (o `AvroSerializer` do Confluent faz o
  registro automaticamente se não existir).
* Para desenvolvimento, a aplicação Flask roda em `debug=True` e host `0.0.0.0`.