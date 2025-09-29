import os
import re
from typing import List, Dict, Optional

class LogService:
    """Classe para analisar logs de producer, consumer e status dos brokers Kafka."""

    def __init__(self, logs_dir: str = "/workspaces/INF1304-T1/logs"):
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
                # Extract partition and offset from the line format:
                # "Mensagem enviada para dados-sensores [partição 0, offset 18636] no broker líder brokerId=3"
                match = re.search(
                    r'Mensagem enviada para dados-sensores \[partição (\d+), offset (\d+)\]',
                    line
                )
                if match:
                    # Since there's no timestamp in the producer log, use current format
                    import datetime
                    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    messages.append({
                        'timestamp': timestamp,
                        'partition': int(match.group(1)),
                        'offset': int(match.group(2)),
                        'type': 'sent',
                        'status': 'success'
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
            # Look for consumer activity - config lines, connection messages, etc.
            if ("bootstrap.servers" in line or
                "ConsumerConfig" in line or
                "group.id" in line or
                "auto.offset.reset" in line):

                # Extract timestamp from log format: "20:12:26.222 [main] INFO ..."
                timestamp_match = re.search(r'(\d{2}:\d{2}:\d{2}\.\d{3})', line)
                if timestamp_match:
                    # Convert to full timestamp format for consistency
                    import datetime
                    today = datetime.datetime.now().strftime('%Y-%m-%d')
                    time_part = timestamp_match.group(1)[:8]  # Remove milliseconds
                    full_timestamp = f"{today} {time_part}"

                    messages.append({
                        'timestamp': full_timestamp,
                        'message': line.strip(),
                        'type': 'received' if 'bootstrap.servers' in line else 'info'
                    })

        return messages

    def get_kafka_broker_status(self) -> Dict[str, str]:
        """Obtém o status de cada broker Kafka"""
        brokers = ['kafka1', 'kafka2', 'kafka3']
        status = {}

        # percorre os logs de cada broker e guarda seu status
        for broker in brokers:
            log_file = f"{broker}.log"
            content = self._read_log_file(log_file)

            if not content:
                status[broker] = "NO_LOGS"
                continue

            # Check for different status indicators in Kafka logs
            lines = content.split('\n')
            broker_status = "UNKNOWN"

            # Look for recent activity (last 50 lines to check current status)
            recent_lines = lines[-50:] if len(lines) > 50 else lines

            # Check for startup completion
            started_found = False
            error_found = False

            for line in recent_lines:
                if not line.strip():
                    continue

                # Check for successful startup indicators
                if any(indicator in line for indicator in [
                    "started (kafka.server.KafkaServer)",
                    "Kafka Server started",
                    "KafkaServer started",
                    "[KafkaServer id="
                ]):
                    started_found = True

                # Check for error indicators
                if any(error in line.upper() for error in ["ERROR", "FATAL", "EXCEPTION"]):
                    error_found = True

            # Check entire log for startup messages if not found in recent lines
            if not started_found:
                for line in lines:
                    if any(indicator in line for indicator in [
                        "started (kafka.server.KafkaServer)",
                        "Kafka Server started",
                        "KafkaServer started"
                    ]):
                        started_found = True
                        break

            # Determine status based on findings
            if error_found:
                broker_status = "ERROR"
            elif started_found:
                broker_status = "RUNNING"
            else:
                # Check if there's any recent activity
                if len(recent_lines) > 0:
                    broker_status = "STARTING"
                else:
                    broker_status = "NO_ACTIVITY"

            status[broker] = broker_status

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

    # ...existing code...

    def get_anomaly_messages(self) -> List[Dict]:
        """Detecta anomalias nos logs do consumer e outros componentes"""
        anomalies = []

        # Check consumer logs for anomalies
        consumer_content = self._read_log_file("consumer.log")
        if consumer_content:
            for line_num, line in enumerate(consumer_content.split('\n'), 1):
                if not line.strip():
                    continue

                # Extract timestamp from consumer log format: "20:12:26.222 [main] INFO ..."
                timestamp_match = re.search(r'(\d{2}:\d{2}:\d{2}\.\d{3})', line)
                timestamp = timestamp_match.group(1)[:8] if timestamp_match else "Unknown"

                # Convert to full timestamp
                if timestamp != "Unknown":
                    import datetime
                    today = datetime.datetime.now().strftime('%Y-%m-%d')
                    full_timestamp = f"{today} {timestamp}"
                else:
                    full_timestamp = "Unknown"

                # Detect different types of anomalies in consumer logs
                anomaly_detected = False
                anomaly_type = ""
                severity = "low"

                # Error level anomalies
                if any(error in line.upper() for error in ['ERROR', 'EXCEPTION', 'FATAL']):
                    anomaly_detected = True
                    anomaly_type = "consumer_error"
                    severity = "high"

                # Warning level anomalies
                elif "WARN" in line.upper():
                    anomaly_detected = True
                    anomaly_type = "consumer_warning"
                    severity = "medium"

                # Connection issues
                elif any(conn in line.lower() for conn in ['connection refused', 'timeout', 'failed to connect', 'network error']):
                    anomaly_detected = True
                    anomaly_type = "connection_issue"
                    severity = "high"

                # Consumer group issues
                elif any(group in line.lower() for group in ['rebalance', 'partition assignment', 'consumer group']):
                    if any(issue in line.lower() for issue in ['failed', 'error', 'timeout']):
                        anomaly_detected = True
                        anomaly_type = "consumer_group_issue"
                        severity = "medium"

                # Offset issues
                elif any(offset in line.lower() for offset in ['offset', 'commit']) and any(issue in line.lower() for issue in ['failed', 'error', 'invalid']):
                    anomaly_detected = True
                    anomaly_type = "offset_issue"
                    severity = "medium"

                # Deserialization errors
                elif any(deser in line.lower() for deser in ['deserialization', 'deserializer', 'parse']) and "error" in line.lower():
                    anomaly_detected = True
                    anomaly_type = "deserialization_error"
                    severity = "high"

                if anomaly_detected:
                    anomalies.append({
                        'timestamp': full_timestamp,
                        'type': anomaly_type,
                        'severity': severity,
                        'message': line.strip(),
                        'source': 'consumer.log',
                        'line': line_num,
                        'component': 'consumer'
                    })

        # Also check producer logs for completeness
        producer_content = self._read_log_file("producer.log")
        if producer_content:
            for line_num, line in enumerate(producer_content.split('\n'), 1):
                if not line.strip():
                    continue

                # Look for errors in producer logs
                if any(error in line.lower() for error in ['error', 'exception', 'failed', 'timeout']):
                    # Extract timestamp if available, otherwise use current time
                    import datetime
                    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    severity = 'high' if any(critical in line.lower() for critical in ['error', 'exception', 'failed']) else 'medium'

                    anomalies.append({
                        'timestamp': timestamp,
                        'type': 'producer_error',
                        'severity': severity,
                        'message': line.strip(),
                        'source': 'producer.log',
                        'line': line_num,
                        'component': 'producer'
                    })

        # Check Kafka broker logs for anomalies
        for broker_file in ['kafka1.log', 'kafka2.log', 'kafka3.log']:
            broker_content = self._read_log_file(broker_file)
            if broker_content:
                for line_num, line in enumerate(broker_content.split('\n'), 1):
                    if not line.strip():
                        continue

                    # Extract timestamp from Kafka log format: [2024-09-29 20:12:26,222]
                    timestamp_match = re.search(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d{3}\]', line)
                    timestamp = timestamp_match.group(1) if timestamp_match else "Unknown"

                    # Detect Kafka broker anomalies
                    if any(error in line.upper() for error in ['ERROR', 'FATAL', 'EXCEPTION']):
                        severity = 'critical' if 'FATAL' in line.upper() else 'high'

                        # Truncate long messages
                        message = line.strip()
                        if len(message) > 150:
                            message = message[:150] + "..."

                        anomalies.append({
                            'timestamp': timestamp,
                            'type': 'broker_error',
                            'severity': severity,
                            'message': message,
                            'source': broker_file,
                            'line': line_num,
                            'component': 'kafka_broker'
                        })

                    # Warn level issues
                    elif 'WARN' in line.upper():
                        message = line.strip()
                        if len(message) > 150:
                            message = message[:150] + "..."

                        anomalies.append({
                            'timestamp': timestamp,
                            'type': 'broker_warning',
                            'severity': 'medium',
                            'message': message,
                            'source': broker_file,
                            'line': line_num,
                            'component': 'kafka_broker'
                        })

        # Sort anomalies by timestamp (newest first) and limit to recent ones
        anomalies.sort(key=lambda x: x['timestamp'] if x['timestamp'] != "Unknown" else "0000-00-00 00:00:00", reverse=True)

        return anomalies[:100]  # Return last 100 anomalies

