# O que escrever

explicar o código
explicar o schema
como funciona o kafka com schema registry e avro
como funciona o código
passo a passo de como usar

# Passo a passo para rodar

1. Subir os containers com `docker compose up -d`
2. Criar o tópico no [kafka UI](http://localhost:8080/)
3. Savar o schema no schema registry, usando a collection do insomnia
4. Rodar a aplicação e enviar os eventos usando o insomnia

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