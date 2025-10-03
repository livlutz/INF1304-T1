import os
import re
from typing import List, Dict, Optional

class LogService:
    """Classe para analisar logs de producer, consumer e status dos brokers Kafka."""

    def __init__(self, logs_dir: str = None):
        """Função para inicializar o serviço de logs com o diretório dos logs.
        Returns:
            type: None
        """
        if logs_dir is None:
            # Pega o diretorio dos logs
            if os.path.exists('/app/logs'):
                logs_dir = '/app/logs'
            else:
                logs_dir = '/workspaces/INF1304-T1/logs'
        self.logs_dir = logs_dir

    def _read_log_file(self, filename: str) -> Optional[str]:
        """Lê o conteúdo do arquivo de log
        Returns:
            type: file content or None
        """
        log_path = os.path.join(self.logs_dir, filename)

        if not os.path.exists(log_path):
            return None

        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                return f.read()

        except Exception as e:
            print(f"Error reading {filename}: {e}")
            return None

    def get_sensors_messages(self) -> List[Dict]:
        """Obtém mensagens de sensores analisadas a partir dos logs
        Returns:
            type: list
        """
        messages = []
        for i in range(1, 4):
            content = self._read_log_file(f"sensor{i}.log")
            if not content:
                continue

            for line in content.split('\n'):
                if "Mensagem enviada para" in line:
                    match = re.search(
                        r'Mensagem enviada para dados-sensores \[partição (\d+), offset (\d+)\]',
                        line
                    )
                    if match:
                        import datetime
                        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        messages.append({
                            'timestamp': timestamp,
                            'partition': int(match.group(1)),
                            'offset': int(match.group(2)),
                            'type': 'sent',
                            'status': 'success',
                            'sensor': f'sensor{i}'
                        })
        return messages

    def get_consumers_messages(self) -> List[Dict]:
        """Obtém mensagens de consumers analisadas a partir dos logs
        Returns:
            type: list
        """
        messages = []
        for i in range(1, 4):
            content = self._read_log_file(f"consumer{i}.log")
            if not content:
                continue

            lines = content.split('\n')
            received_count = sum(1 for line in lines if "Received sensor data: SensorData" in line)
            print(f"DEBUG: Consumer{i} has {len(lines)} total lines and {received_count} received messages", flush=True)

            for line in content.split('\n'):
                if "Received sensor data: SensorData" in line:
                    timestamp_match = re.search(r'(\d{2}:\d{2}:\d{2}\.\d{3})', line)
                    if timestamp_match:
                        import datetime
                        today = datetime.datetime.now().strftime('%Y-%m-%d')
                        time_part = timestamp_match.group(1)[:8]
                        full_timestamp = f"{today} {time_part}"

                        machine_match = re.search(r"idMaquina='([^']+)'", line)
                        machine_id = machine_match.group(1) if machine_match else "Unknown"

                        sector_match = re.search(r"setor='([^']+)'", line)
                        sector = sector_match.group(1) if sector_match else "Unknown"

                        messages.append({
                            'timestamp': full_timestamp,
                            'message': line.strip(),
                            'type': 'received',
                            'machine_id': machine_id,
                            'sector': sector,
                            'consumer': f'consumer{i}'
                        })
        return messages

    def get_kafka_broker_status(self) -> Dict[str, str]:
        """Obtém o status de cada broker Kafka a partir da última mensagem de log relevante.
        Returns:
            type: dict
        """
        brokers = ['kafka1', 'kafka2', 'kafka3']
        status = {}

        for broker in brokers:
            log_file = f"{broker}.log"
            content = self._read_log_file(log_file)

            if content is None:
                status[broker] = "LOG_CLEARED"
                continue

            lines = content.strip().split('\n')
            broker_status = "UNKNOWN"

            startup_indicators = [
                "started (kafka.server.KafkaServer)", "Kafka Server started",
                "KafkaServer started", "[KafkaServer id=", "[KafkaRaftServer nodeId=",
                "Transition from STARTING to STARTED", "BrokerServer id=", "Endpoint is now READY",
                "Scheduling unloading","Ignored unloading metadata for", "recuperado"
            ]
            shutdown_indicators = ["shutting down", "Shutdown completed","derrubado"]
            error_indicators = ["FATAL", "CONTAINER_REMOVED"]

            for line in reversed(lines):
                if not line.strip():
                    continue

                if any(indicator in line.upper() for indicator in error_indicators):
                    broker_status = "KILLED"
                    break

                if any(indicator in line for indicator in shutdown_indicators):
                    broker_status = "STOPPED"
                    break

                if any(indicator in line for indicator in startup_indicators):
                    broker_status = "RUNNING"
                    break

            if broker_status == "UNKNOWN" and lines and any(line.strip() for line in lines):
                broker_status = "STARTING"

            status[broker] = broker_status

        return status

    def get_services_status(self) -> Dict[str, str]:
        """Obtém o status de cada sensor e consumer a partir da última mensagem de log relevante.
        Returns:
            type: dict
        """
        services = ['sensor1', 'sensor2', 'sensor3', 'consumer1', 'consumer2', 'consumer3']
        status = {}

        for service in services:
            log_file = f"{service}.log"
            content = self._read_log_file(log_file)

            if content is None:
                status[service] = "LOG_CLEARED"
                continue

            lines = content.strip().split('\n')
            service_status = "UNKNOWN"

            startup_indicators = [
                "Conectado ao Kafka", "Sensor configurado para a partição",
                "Consumidor iniciado", "atribuído à partição", "recuperado"
            ]
            shutdown_indicators = ["shutting down", "Shutdown completed"]
            error_indicators = ["FATAL", "EXCEPTION", "Error", "Falha","derrubado"]

            for line in reversed(lines):
                if not line.strip():
                    continue

                if any(indicator in line for indicator in error_indicators):
                    service_status = "ERROR"
                    break

                if any(indicator in line for indicator in shutdown_indicators):
                    service_status = "STOPPED"
                    break

                if any(indicator in line for indicator in startup_indicators):
                    service_status = "RUNNING"
                    break

            if service_status == "UNKNOWN" and lines and any(line.strip() for line in lines):
                service_status = "STARTING"

            status[service] = service_status

        return status

    def get_system_stats(self) -> Dict:
        """Obtém estatísticas gerais do sistema a partir dos logs
        Returns:
            type: dict
        """
        sensors_msgs = self.get_sensors_messages()
        consumers_msgs = self.get_consumers_messages()
        received_msgs = [m for m in consumers_msgs if m['type'] == 'received']

        stats = {
            'total_sent': len(sensors_msgs),
            'total_received': len(received_msgs),
            'last_sent': sensors_msgs[-1] if sensors_msgs else None,
            'last_received': received_msgs[-1] if received_msgs else None,
            'kafka_brokers': self.get_kafka_broker_status(),
            'services': self.get_services_status()
        }

        return stats

    def get_recent_activity(self, limit: int = 10) -> List[Dict]:
        """Obtém a atividade recente a partir de todos os logs
        Returns:
            type: list
        """
        sensors_msgs = self.get_sensors_messages()
        consumers_msgs = self.get_consumers_messages()

        all_msgs = sensors_msgs + consumers_msgs
        all_msgs.sort(key=lambda x: x['timestamp'], reverse=True)

        return all_msgs[:limit]

    def get_anomaly_messages(self) -> List[Dict]:
        """Detecta anomalias nos logs do consumer e outros componentes
        Returns:
            type: list
        """
        anomalies = []

        for i in range(1, 4):
            consumer_content = self._read_log_file(f"consumer{i}.log")
            if consumer_content:
                for line_num, line in enumerate(consumer_content.split('\n'), 1):
                    if not line.strip():
                        continue

                    timestamp_match = re.search(r'(\d{2}:\d{2}:\d{2}\.\d{3})', line)
                    timestamp = timestamp_match.group(1)[:8] if timestamp_match else "Unknown"

                    if timestamp != "Unknown":
                        import datetime
                        today = datetime.datetime.now().strftime('%Y-%m-%d')
                        full_timestamp = f"{today} {timestamp}"
                    else:
                        full_timestamp = "Unknown"

                    anomaly_detected = False
                    anomaly_type = ""
                    severity = "low"

                    if any(error in line.upper() for error in ['KILLED', 'EXCEPTION', 'FATAL']):
                        anomaly_detected = True
                        anomaly_type = "consumer_error"
                        severity = "critical" if (("FATAL" in line.upper()) or ("KILLED" in line.upper())) else "high"

                    elif "WARN" in line.upper():
                        anomaly_detected = True
                        anomaly_type = "sensor_anomaly"
                        severity = "medium"

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
                        elif "Low energy consumption detected" in line:
                            anomaly_type = "low_energy"
                            severity = "low"
                        else:
                            anomaly_type = "sensor_warning"

                    if anomaly_detected:
                        machine_id = "Unknown"
                        sector = "Unknown"

                        machine_match = re.search(r'Machine:\s*([^,]+)', line)
                        if machine_match:
                            machine_id = machine_match.group(1).strip()

                        sector_match = re.search(r'Sector:\s*([^,]+)', line)
                        if sector_match:
                            sector = sector_match.group(1).strip()

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

                        anomalies.append({
                            'timestamp': full_timestamp,
                            'type': anomaly_type,
                            'severity': severity,
                            'message': line.strip(),
                            'source': f'consumer{i}.log',
                            'line': line_num,
                            'component': f'consumer{i}',
                            'machine_id': machine_id,
                            'sector': sector,
                            'sensor_value': sensor_value
                        })

        for i in range(1, 4):
            producer_content = self._read_log_file(f"sensor{i}.log")
            if producer_content:
                for line_num, line in enumerate(producer_content.split('\n'), 1):
                    if not line.strip():
                        continue

                    if any(error in line.lower() for error in ['error', 'exception', 'failed', 'timeout']):
                        import datetime
                        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                        severity = 'high' if any(critical in line.lower() for critical in ['error', 'exception', 'failed']) else 'medium'

                        anomalies.append({
                            'timestamp': timestamp,
                            'type': 'producer_error',
                            'severity': severity,
                            'message': line.strip(),
                            'source': f'sensor{i}.log',
                            'line': line_num,
                            'component': f'sensor{i}'
                        })

        for broker_file in ['kafka1.log', 'kafka2.log', 'kafka3.log']:
            broker_content = self._read_log_file(broker_file)
            if broker_content:
                for line_num, line in enumerate(broker_content.split('\n'), 1):
                    if not line.strip():
                        continue

                    timestamp_match = re.search(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d{3}\]', line)
                    timestamp = timestamp_match.group(1) if timestamp_match else "Unknown"

                    if any(error in line.upper() for error in ['ERROR', 'FATAL', 'EXCEPTION', 'KILLED']):
                        severity = 'critical'
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

        anomalies.sort(key=lambda x: x['timestamp'] if x['timestamp'] != "Unknown" else "0000-00-00 00:00:00", reverse=True)

        return anomalies[:100]