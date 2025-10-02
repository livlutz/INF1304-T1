
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

## 📋 Critério para determinação de anomalias

O sistema detecta anomalias baseado em:
- Valores de temperatura fora do range esperado (>80°C ou <10°C)
- Variações bruscas de pressão
- Padrões anômalos de vibração
- Falhas de comunicação entre sensores e consumidores

## 🚀 Instalação da Aplicação

### Pré-requisitos

- **Docker** >= 20.10
- **Docker Compose** >= 2.0
- **Make** (opcional, mas recomendado)
- **Git**

### 1. Clone o Repositório

```bash
git clone https://github.com/livlutz/INF1304-T1.git
cd INF1304-T1
```

### 2. Verificar Dependências

Certifique-se de que o Docker está rodando:

```bash
docker --version
docker-compose --version
```

### 3. Construir e Iniciar o Sistema

#### Opção A: Usando Makefile (Recomendado)

```bash
# Iniciar todo o sistema
make all

# Ou individualmente:
make build    # Constrói todas as imagens
make up       # Inicia todos os containers
make logs     # Exibe logs em tempo real
```

#### Opção B: Usando Docker Compose diretamente

```bash
# Construir imagens
docker-compose build

# Iniciar serviços
docker-compose up -d

# Ver logs
docker-compose logs -f
```

## 🎮 Instruções de Operação

### Dashboard de Monitoramento

1. **Acesse o Dashboard**: Abra `http://localhost:8501` no navegador
2. **Recursos disponíveis**:
   - Status dos brokers Kafka (kafka1, kafka2, kafka3)
   - Métricas dos sensores e consumidores
   - Anomalias detectadas
   - Atividade recente do sistema

### Comandos Principais

#### Inicialização Completa
```bash
make all          # Constrói, inicia e exibe logs
```

#### Gerenciamento de Serviços
```bash
make up           # Inicia todos os containers
make down         # Para todos os containers
make clean        # Remove containers e imagens
```

#### Monitoramento
```bash
make logs                    # Logs de todos os serviços
make logs-frontend          # Logs apenas do dashboard
make logs-sensors           # Logs dos sensores
make logs-consumers         # Logs dos consumidores
make logs-kafka             # Logs dos brokers Kafka
```

#### Simulação de Falhas
```bash
make failure                # Simula falha aleatória (broker ou consumidor)
make recovery               # Recupera serviços com falha
```

### Verificação do Sistema

#### Verificar Status dos Containers
```bash
docker-compose ps
```

#### Verificar Logs Específicos
```bash
docker logs consumer1
docker logs consumer2
docker logs consumer3
docker logs sensor1
docker logs sensor2
docker logs sensor3
docker logs kafka1
docker logs kafka2
docker logs kafka3
```

### Resolução de Problemas

#### Se os containers não iniciarem:
```bash
make clean
make all
```

#### Se as mensagens não estiverem sendo distribuídas:
```bash
# Verificar se o tópico tem 3 partições
docker exec -it kafka1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --describe --topic dados-sensores

# Recriar tópico se necessário
docker exec -it kafka1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --delete --topic dados-sensores
docker exec -it kafka1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic dados-sensores --partitions 3 --replication-factor 2
```

#### Reset do Sistema
```bash
make clean        # Remove tudo
make all          # Reconstrói do zero
```

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

