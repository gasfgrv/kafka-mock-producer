#!/bin/bash

echo "Criando tópico..."
kafka-topics --create \
    --bootstrap-server kafka:29092 \
    --replication-factor 1 \
    --partitions 1 \
    --topic usuarios

echo "Tópico criado com sucesso!"