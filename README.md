
# INF1304-T1
## 🏭 Projeto Kafka Fábrica Inteligente

Sistema de monitoramento de sensores em uma fábrica inteligente utilizando **Apache Kafka** em um cluster **Docker**.
O objetivo é garantir **balanceamento de carga**, **tolerância a falhas** e **failover automático** entre consumidores e brokers.

---

## 📌 Objetivo

- Criar um cluster Kafka com múltiplos brokers.
- Simular sensores como produtores Kafka.
- Implementar consumidores Kafka em Java com balanceamento automático.
- Registrar dados e alertas em banco de dados.
- Demonstrar falhas e rebalanceamento automático.

---

## Critério para determinação de anomalias

temperatura > 50 graus celsius - alta
temperatura < 10 graus celsius - baixa
vibracao > 4.0 - alta
vibracao < 1.0 - baixa
consumo de energia > 400 - alto
consumo de energia < 80 - baixo



## 🗂 Arquitetura de Diretórios

```bash
projeto-kafka-fabrica/
│
├── backend-java/                  # Backend - processadores Kafka
│   ├── src/
│   │   └── main/
│   │       ├── java/
│   │       │   └── com/fabrica/monitoramento/
│   │       │       ├── consumer/       # Consumidores Kafka
│   │       │       ├── service/        # Lógica de análise (anomalias etc.)
│   │       │       ├── model/          # DTOs/entidades
│   │       │       └── repository/     # Persistência no banco
│   │       └── resources/
│   │           ├── application.properties   # Configuração Kafka, DB
│   │           └── logback.xml              # Logs de dados
│   ├── pom.xml
│   └── Dockerfile
│
├── frontend-python/               # Dashboard / visualização
│   ├── app/
│   │   ├── main.py
│   │   ├── services/               # Conexão ao banco de dados
│   │   ├── views/                  # Páginas/telas
│   │   └── static/                 # HTML/CSS/JS
│   ├── requirements.txt
│   └── Dockerfile
│
├── sensor/                       # Produtores (simulação)
│   ├── sensor.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── db/                            # Banco de dados (Postgres ou outro)
│   └── Dockerfile
│
├── docker-compose.yml             # Orquestra todos os serviços
├── Makefile                       # Atalhos de build/run
├── scripts/                       # Simulação de falhas
│   ├── kill-broker.sh
│   ├── kill-consumer.sh
└── logs/                          # Logs de execução dos Dockers

