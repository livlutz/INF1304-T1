"""Gerar dados periodicos (Json)
    Uma fábrica inteligente possui diversas máquinas espalhadas em diferentes setores (linha de produção,
refrigeração, empacotamento, etc.). Cada máquina é equipada com sensores que enviam dados (temperatura,
vibração, consumo de energia, etc.) continuamente para um sistema central que processa esses dados em tempo
real para detectar anomalias, falhas ou padrões de uso.
"""

import json
import random
import time
from datetime import datetime
from kafka import KafkaProducer

# Configurações da simulação
SETORES = ["linha_producao", "refrigeracao", "empacotamento"]

#podemos alterar esse numero
NUMERO_MAQUINAS_POR_SETOR = 5

TIPOS_SENSORES = {
    "temperatura": {"min": 20.0, "max": 80.0, "unidade": "C"},
    "vibracao": {"min": 0.5, "max": 5.0, "unidade": "mm/s"},
    "consumo_energia": {"min": 50.0, "max": 500.0, "unidade": "kW"}
}

#dados-sensores sera o nome do topico kafka que o sensor vai enviar as mensagens
NOME_ARQUIVO = "info_sensores.json"

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

        # Cria um nome de arquivo único com base no timestamp
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo_com_timestamp = f"dados_sensores_{timestamp_str}.json"

        try:
            with open(nome_arquivo_com_timestamp, "w") as f:
                json.dump(dados_coletados, f, indent=4)
            print(f"Arquivo '{nome_arquivo_com_timestamp}' gerado com sucesso!")

        except IOError as e:
            print(f"Erro ao escrever o arquivo: {e}")

if __name__ == "__main__":
    # Gera um único arquivo JSON ao executar o script
    #gerar_arquivos_json(num_arquivos=1)

    # Para simular a geração contínua
    while True:
        gerar_arquivos_json(num_arquivos=1)
        #manda mensagem ao kafka
        producer = KafkaProducer(bootstrap_servers='kafka1:9092')

        with open(NOME_ARQUIVO, "r") as f:
            dados_coletados = json.load(f)

        for dados in dados_coletados:
            producer.send('dados-sensores', json.dumps(dados).encode('utf-8'))

        producer.close()
        
        time.sleep(5)  # Espera 5 segundos antes de gerar o próximo arquivo