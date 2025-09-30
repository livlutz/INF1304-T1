import os
import re
from typing import List, Dict, Optional

class LogService:
    """Classe para analisar logs de producer, consumer e status dos brokers Kafka."""

    def __init__(self, logs_dir: str = None):
        """Função para inicializar o serviço de logs com o diretório dos logs."""
        if logs_dir is None:
            # Auto-detect the correct logs directory based on environment
            if os.path.exists('/app/logs'):
                # Running inside Docker container
                logs_dir = '/app/logs'
            else:
                # Running in development environment
                logs_dir = '/workspaces/INF1304-T1/logs'
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
            # Look for actual sensor data processing messages
            if "Received sensor data: SensorData" in line:
                # Extract timestamp from log format: "16:09:49.973 [main] INFO ..."
                timestamp_match = re.search(r'(\d{2}:\d{2}:\d{2}\.\d{3})', line)
                if timestamp_match:
                    # Convert to full timestamp format for consistency
                    import datetime
                    today = datetime.datetime.now().strftime('%Y-%m-%d')
                    time_part = timestamp_match.group(1)[:8]  # Remove milliseconds
                    full_timestamp = f"{today} {time_part}"

                    # Extract machine ID from the sensor data
                    machine_match = re.search(r"idMaquina='([^']+)'", line)
                    machine_id = machine_match.group(1) if machine_match else "Unknown"

                    # Extract sector from the sensor data
                    sector_match = re.search(r"setor='([^']+)'", line)
                    sector = sector_match.group(1) if sector_match else "Unknown"

                    messages.append({
                        'timestamp': full_timestamp,
                        'message': line.strip(),
                        'type': 'received',
                        'machine_id': machine_id,
                        'sector': sector
                    })

            # Also look for configuration messages as secondary info
            elif ("bootstrap.servers" in line or
                  "ConsumerConfig" in line or
                  "group.id" in line or
                  "auto.offset.reset" in line):

                # Extract timestamp from log format: "16:09:19.609 [main] INFO ..."
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
                        'type': 'config'
                    })

        return messages

    def get_kafka_broker_status(self) -> Dict[str, str]:
        """Obtém o status de cada broker Kafka a partir da última mensagem de log relevante."""
        brokers = ['kafka1', 'kafka2', 'kafka3']
        status = {}

        for broker in brokers:
            log_file = f"{broker}.log"
            content = self._read_log_file(log_file)

            # If the log file does not exist, it means the broker has been stopped
            if content is None:
                status[broker] = "LOG_CLEARED"  # New status for cleared logs
                continue

            lines = content.strip().split('\n')
            broker_status = "UNKNOWN"

            # Palavras-chave para busca
            startup_indicators = [
                "started (kafka.server.KafkaServer)", "Kafka Server started",
                "KafkaServer started", "[KafkaServer id=", "[KafkaRaftServer nodeId=",
                "Transition from STARTING to STARTED", "BrokerServer id=", "Endpoint is now READY"
            ]
            shutdown_indicators = ["shutting down", "Shutdown completed", "Killing broker container"]
            error_indicators = ["FATAL", "CONTAINER_REMOVED"]

            # Itera de trás para frente para encontrar o status mais recente
            for line in reversed(lines):
                if not line.strip():
                    continue

                # Verifica por erros fatais
                if any(indicator in line.upper() for indicator in error_indicators):
                    broker_status = "KILLED"
                    break  # Encontrou o status mais recente

                # Verifica por mensagens de shutdown
                if any(indicator in line for indicator in shutdown_indicators):
                    broker_status = "STOPPED"
                    break

                # Verifica por mensagens de startup
                if any(indicator in line for indicator in startup_indicators):
                    broker_status = "RUNNING"
                    break

            if broker_status == "UNKNOWN" and lines and any(line.strip() for line in lines):
                broker_status = "STARTING"

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
                if any(error in line.upper() for error in ['KILLED', 'EXCEPTION', 'FATAL']):
                    anomaly_detected = True
                    anomaly_type = "consumer_error"
                    severity = "high"

                # Warning level anomalies - look for specific sensor anomalies
                elif "WARN" in line.upper():
                    anomaly_detected = True
                    anomaly_type = "sensor_anomaly"
                    severity = "medium"

                    # Determine specific anomaly type based on content
                    if "High temperature detected" in line:
                        anomaly_type = "high_temperature"
                        severity = "high"
                    elif "Low temperature detected" in line:
                        anomaly_type = "low_temperature"
                        severity = "medium"
                    elif "High vibration detected" in line:
                        anomaly_type = "high_vibration"
                        severity = "high"
                    elif "Low vibration detected" in line:
                        anomaly_type = "low_vibration"
                        severity = "low"
                    elif "High energy consumption detected" in line:
                        anomaly_type = "high_energy"
                        severity = "high"
                    elif "High pressure detected" in line:
                        anomaly_type = "high_pressure"
                        severity = "medium"
                    elif "Low pressure detected" in line:
                        anomaly_type = "low_pressure"
                        severity = "medium"
                    else:
                        anomaly_type = "sensor_warning"

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
                    # Extract machine and sector information if available
                    machine_id = "Unknown"
                    sector = "Unknown"

                    # Look for machine and sector in the message
                    machine_match = re.search(r'Machine:\s*([^,]+)', line)
                    if machine_match:
                        machine_id = machine_match.group(1).strip()

                    sector_match = re.search(r'Sector:\s*([^,]+)', line)
                    if sector_match:
                        sector = sector_match.group(1).strip()

                    # Extract the specific value and unit for sensor anomalies
                    sensor_value = None
                    if "Temperature:" in line:
                        temp_match = re.search(r'Temperature:\s*([\d.]+)', line)
                        if temp_match:
                            sensor_value = f"{temp_match.group(1)}°C"
                    elif "Vibration:" in line:
                        vib_match = re.search(r'Vibration:\s*([\d.]+)', line)
                        if vib_match:
                            sensor_value = f"{vib_match.group(1)} mm/s"
                    elif "Energy Consumption:" in line:
                        energy_match = re.search(r'Energy Consumption:\s*([\d.]+)', line)
                        if energy_match:
                            sensor_value = f"{energy_match.group(1)} kW"
                    elif "Pressure:" in line:
                        pressure_match = re.search(r'Pressure:\s*([\d.]+)', line)
                        if pressure_match:
                            sensor_value = f"{pressure_match.group(1)} bar"

                    anomalies.append({
                        'timestamp': full_timestamp,
                        'type': anomaly_type,
                        'severity': severity,
                        'message': line.strip(),
                        'source': 'consumer.log',
                        'line': line_num,
                        'component': 'consumer',
                        'machine_id': machine_id,
                        'sector': sector,
                        'sensor_value': sensor_value
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

