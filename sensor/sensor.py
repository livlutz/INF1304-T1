"""Gerar dados periodicos (Json)
    Uma fábrica inteligente possui diversas máquinas espalhadas em diferentes setores (linha de produção,
refrigeração, empacotamento, etc.). Cada máquina é equipada com sensores que enviam dados (temperatura,
vibração, consumo de energia, etc.) continuamente para um sistema central que processa esses dados em tempo
real para detectar anomalias, falhas ou padrões de uso.
"""
import os
import sys
import json
import random
import time
from datetime import datetime
from kafka import KafkaProducer,KafkaAdminClient
from kafka.structs import TopicPartition

sys.stdout.reconfigure(line_buffering=True)

# Configurações da simulação
SETORES = ["linha_producao", "refrigeracao", "empacotamento"]

TIPOS_SENSORES = {
    "temperatura": {"min": 20.0, "max": 80.0, "unidade": "C"},
    "vibracao": {"min": 0.5, "max": 5.0, "unidade": "mm/s"},
    "consumo_energia": {"min": 50.0, "max": 500.0, "unidade": "kW"}
}

#dados-sensores sera o nome do topico kafka que o sensor vai enviar as mensagens
NOME_ARQUIVO = "dados-sensores.json"
KAFKA_BROKERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka1:9092").split(",")
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'dados-sensores')

def gerar_dados_maquina():
    """
    Gera um conjunto de dados simulados para uma única máquina.
    """
    dados_maquina = {
        "id_maquina": f"maquina_{random.randint(1, 100)}",
        "setor": random.choice(SETORES),
        "timestamp": datetime.now().isoformat(),
        "sensores": {}
    }

    for sensor, config in TIPOS_SENSORES.items():
        # Gera um valor aleatório dentro do intervalo definido
        valor = round(random.uniform(config["min"], config["max"]), 2)
        dados_maquina["sensores"][sensor] = {
            "valor": valor,
            "unidade": config["unidade"]
        }

    return dados_maquina

def gerar_arquivos_json(num_arquivos=1):
    """
    Gera um ou mais arquivos JSON com dados simulados.
    Cada arquivo contém dados de um número aleatório de máquinas.
    """
    for i in range(num_arquivos):
        # Gera um número aleatório de registros para o arquivo
        num_registros = random.randint(10, 20)
        dados_coletados = [gerar_dados_maquina() for _ in range(num_registros)]

        try:
            with open(NOME_ARQUIVO, "w") as f:
                json.dump(dados_coletados, f, indent=4)
            print(f"Arquivo '{NOME_ARQUIVO}' gerado com sucesso!")

        except IOError as e:
            print(f"Erro ao escrever o arquivo: {e}")

def criar_producer(retries=10, delay=5):
    """"
    Cria um KafkaProducer com tentativas de reconexão.
    retries: número de tentativas
    delay: tempo de espera entre tentativas (em segundos)
    Retorna o producer se a conexão for bem-sucedida, caso contrário, levanta uma exceção.
    """
    for i in range(retries):
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKERS,
                retries=5
            )
            print(f"Conectado ao Kafka! Brokers tentados: {KAFKA_BROKERS}", flush=True)
            return producer
        except Exception as e:
            print(f"Tentativa {i+1}/{retries} falhou: {e}", flush=True)
            time.sleep(delay)
    raise Exception("Não foi possível conectar ao Kafka.")

def obter_lider(topico, particao):
    try:
        admin = KafkaAdminClient(bootstrap_servers=KAFKA_BROKERS, client_id="sensor-admin")
        topics = admin.describe_topics([topico])
        for t in topics:
            for p in t["partitions"]:
                if p["partition"] == particao:
                    leader = p["leader"]
                    if leader != -1:  # -1 significa sem líder
                        broker = next(b for b in t["partitions"] if b["partition"] == particao)
                        return f"brokerId={leader}"
        return "desconhecido (sem líder definido)"
    except Exception as e:
        return f"desconhecido ({e})"
    
if __name__ == "__main__":
    # Para simular a geração contínua
    while True:
        gerar_arquivos_json(num_arquivos=1)
        #manda mensagem ao kafka

        producer = criar_producer()

        with open(NOME_ARQUIVO, "r") as f:
            dados_coletados = json.load(f)

        for dados in dados_coletados:
            future = producer.send(KAFKA_TOPIC, json.dumps(dados).encode('utf-8'))
            result = future.get(timeout=10)
            lider = obter_lider(result.topic, result.partition) 
            print(
                f"Mensagem enviada para {result.topic} [partição {result.partition}, offset {result.offset}] "
                f"no broker líder {lider}",
                flush=True
            )

        producer.close()

        # Exclui o arquivo após enviar todas as informações ao Kafka
        try:
            os.remove(NOME_ARQUIVO)
            print(f"Arquivo '{NOME_ARQUIVO}' excluído com sucesso!")
        except OSError as e:
            print(f"Erro ao excluir o arquivo: {e}")

        time.sleep(5)