
# INF1304-T1
## 🏭 Projeto Kafka Fábrica Inteligente

Sistema de monitoramento de sensores em uma fábrica inteligente utilizando **Apache Kafka** em um cluster **Docker**.
O objetivo é garantir **balanceamento de carga**, **tolerância a falhas** e **failover automático** entre consumidores e brokers.

---

![Contributors](https://img.shields.io/github/contributors/livlutz/INF1304-T1)
![Java](https://img.shields.io/badge/language-Java-red.svg)
![Python](https://img.shields.io/badge/python-3670A0?style=plastic&logo=python&logoColor=ffdd54)
![Bash](https://img.shields.io/badge/language-Bash-green.svg)
![Languages Count](https://img.shields.io/github/languages/count/livlutz/INF1304-T1)
![GitHub stars](https://img.shields.io/github/stars/livlutz/INF1304-T1?style=social)

## 🤝 Membros da dupla

Lívia Lutz dos Santos - 2211055

Thiago Pereira Camerato - 2212580

## 📌 Objetivo

- Criar um cluster Kafka com múltiplos brokers.
- Simular sensores como produtores Kafka.
- Implementar consumidores Kafka em Java com balanceamento automático.
- Registrar dados e alertas em banco de dados.
- Demonstrar falhas e rebalanceamento automático.

---

## Critério para determinação de anomalias

TODO: completar



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

