import os
import re
from typing import List, Dict, Optional
from datetime import datetime

class LogService:
    """Classe para analisar logs de producer, consumer e status dos brokers Kafka."""

    def __init__(self, logs_dir: str = "../../logs"):
        """Função para inicializar o serviço de logs com o diretório dos logs."""
        self.logs_dir = logs_dir

    def _read_log_file(self, filename: str) -> Optional[str]:
        """Lê o conteúdo do arquivo de log"""
        log_path = os.path.join(self.logs_dir, filename)

        if not os.path.exists(log_path):
            return None

        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                return f.read()

        except Exception as e:
            print(f"Error reading {filename}: {e}")
            return None

    def get_producer_messages(self) -> List[Dict]:
        """Obtém mensagens de producer analisadas a partir dos logs"""
        content = self._read_log_file("producer.log")
        if not content:
            return []

        messages = []

        # montando as mensagens de log do producer
        for line in content.split('\n'):
            if "Mensagem enviada para" in line:
                match = re.search(
                    r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*dados-sensores.*partição (\d+).*offset (\d+)',
                    line
                )
                if match:
                    messages.append({
                        'timestamp': match.group(1),
                        'partition': int(match.group(2)),
                        'offset': int(match.group(3)),
                        'type': 'sent'
                    })
        return messages

    def get_consumer_messages(self) -> List[Dict]:
        """Obtém mensagens de consumer analisadas a partir dos logs"""
        content = self._read_log_file("consumer.log")
        if not content:
            return []

        messages = []

        # montando as mensagens de log do consumer
        for line in content.split('\n'):
            if "Received sensor data" in line or "Consumer started" in line:
                timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                if timestamp_match:
                    messages.append({
                        'timestamp': timestamp_match.group(1),
                        'message': line.strip(),
                        'type': 'received' if 'Received' in line else 'info'
                    })

        return messages

    def get_kafka_broker_status(self) -> Dict[str, str]:
        """Obtém o status de cada broker Kafka"""
        brokers = ['kafka1', 'kafka2', 'kafka3']
        status = {}

        # percorre os logs de cada broker e guarda seu status
        for broker in brokers:
            content = self._read_log_file(f"{broker}.log")
            if not content:
                status[broker] = "NO_LOGS"
                continue

            if "started (kafka.server.KafkaServer)" in content:
                status[broker] = "RUNNING"

            elif "ERROR" in content:
                status[broker] = "ERROR"

            elif "Starting" in content:
                status[broker] = "STARTING"

            else:
                status[broker] = "UNKNOWN"

        return status

    def get_system_stats(self) -> Dict:
        """Obtém estatísticas gerais do sistema a partir dos logs"""
        producer_msgs = self.get_producer_messages()
        consumer_msgs = self.get_consumer_messages()
        received_msgs = [m for m in consumer_msgs if m['type'] == 'received']

        # monta o dicionario de estatisticas
        stats = {
            'total_sent': len(producer_msgs),
            'total_received': len(received_msgs),
            'last_sent': producer_msgs[-1] if producer_msgs else None,
            'last_received': received_msgs[-1] if received_msgs else None,
            'kafka_brokers': self.get_kafka_broker_status()
        }

        return stats

    def get_recent_activity(self, limit: int = 10) -> List[Dict]:
        """Obtém a atividade recente a partir de todos os logs"""
        producer_msgs = self.get_producer_messages()
        consumer_msgs = self.get_consumer_messages()

        # Combina e ordena por timestamp
        all_msgs = producer_msgs + consumer_msgs
        all_msgs.sort(key=lambda x: x['timestamp'], reverse=True)

        return all_msgs[:limit]