"""
Dashboard de Monitoramento Kafka

Este módulo implementa um dashboard interativo usando Streamlit para monitorar
o sistema de sensores, consumidores Kafka, brokers e detectar anomalias em tempo real.
"""

import os
import time
import json
import tempfile
import streamlit as st
from services.log_service import LogService

# Configure Streamlit page
st.set_page_config(
    page_title="Kafka Monitoring Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

class LogAnalyzer:
    """
    Classe responsável por analisar logs do sistema de monitoramento.

    Esta classe centraliza a leitura e análise dos logs de sensores, consumidores Kafka,
    brokers e anomalias, fornecendo métodos para extrair informações e exibir
    um dashboard interativo com Streamlit.

    Attributes:
        log_service (LogService): Instância do serviço de logs para leitura dos arquivos.
    """
    def __init__(self, logs_dir=None):
        """Inicializa o analisador de logs.

        Args:
            logs_dir (str, optional): Diretório dos logs. Padrão é None.
        """
        if logs_dir is None:
            # Detecta o diretório de logs no ambiente
            if os.path.exists('/app/logs'):
                # Executando dentro do container Docker
                logs_dir = '/app/logs'
            else:
                # Executando em ambiente de desenvolvimento
                logs_dir = '/workspaces/INF1304-T1/logs'
        self.log_service = LogService(logs_dir)

    def read_sensors_logs(self):
        """Lê e analisa logs dos sensores

        Returns:
            list: Lista de mensagens dos sensores
        """
        return self.log_service.get_sensors_messages()

    def read_consumers_logs(self):
        """Lê e analisa logs dos consumidores
        Returns:
            list: Lista de mensagens dos consumidores
        """
        return self.log_service.get_consumers_messages()

    def get_kafka_status(self):
        """ Pega os status dos kafkas
        Returns:
            list: Lista de status dos brokers Kafka
        """
        return self.log_service.get_kafka_broker_status()

    def get_services_status(self):
        """ Pega os status dos serviços (sensores e consumidores)
        Returns:
            list: Lista de status dos serviços
        """
        return self.log_service.get_services_status()

    def get_anomaly_messages(self):
        """ Pega as mensagens de anomalias detectadas
        Returns:
            list: Lista de mensagens de anomalias
        """
        return self.log_service.get_anomaly_messages()

    def display_streamlit_dashboard(self):
        """Exibe o dashboard usando Streamlit"""

        # Main title
        st.title("📊 Kafka Monitoring Dashboard")
        st.markdown("---")

        # Get data
        kafka_status = self.get_kafka_status()
        services_status = self.get_services_status()
        sensors_msgs = self.read_sensors_logs()
        consumers_msgs = self.read_consumers_logs()
        received_msgs = [m for m in consumers_msgs if m['type'] == 'received']
        anomalies = self.get_anomaly_messages()

        # Create columns for layout
        col1, col2, col3 = st.columns(3)

        # Kafka Brokers Status
        with col1:
            st.subheader("🔧 Kafka Brokers Status")
            for broker, status in kafka_status.items():
                if status == "RUNNING":
                    st.success(f"● {broker}: {status}")
                elif status == "KILLED":
                    st.error(f"● {broker}: {status}")
                elif status == "STOPPED":
                    st.warning(f"● {broker}: {status}")
                elif status == "LOG_CLEARED":
                    st.info(f"⚪️ {broker}: LOG CLEARED")
                else:
                    st.warning(f"● {broker}: {status}")

        # Services Status
        with col2:
            st.subheader("⚙️ Services Status")
            # Separa sensores e  consumers para display
            sensors_status = {k: v for k, v in services_status.items() if 'sensor' in k}
            consumers_status = {k: v for k, v in services_status.items() if 'consumer' in k}

            st.markdown("**Sensors**")
            for service, status in sensors_status.items():
                if status == "RUNNING":
                    st.success(f"● {service}: {status}")
                elif status == "ERROR":
                    st.error(f"● {service}: {status}")
                else:
                    st.warning(f"● {service}: {status}")

            st.markdown("**Consumers**")
            for service, status in consumers_status.items():
                if status == "RUNNING":
                    st.success(f"● {service}: {status}")
                elif status == "ERROR":
                    st.error(f"● {service}: {status}")
                else:
                    st.warning(f"● {service}: {status}")


        # Stats
        with col3:
            st.subheader("📈 Global Stats")
            # Mensagens por Sensor             st.markdown("**Messages per Sensor**")
            sensor_cols = st.columns(3)
            total_sensor_msgs = 0
            for i in range(1, 4):
                sensor_name = f"sensor{i}"
                count = len([m for m in sensors_msgs if m.get('sensor') == sensor_name])
                total_sensor_msgs += count
                with sensor_cols[i-1]:
                    st.metric(f"Sensor {i}", count)

            # Total de  mensagens sent by all sensors
            st.markdown(f"**Total Messages Sent by All Sensors: {total_sensor_msgs}**")

            # Mensagens por Consumer
            st.markdown("**Messages per Consumer**")
            consumer_cols = st.columns(3)
            total_consumer_msgs = 0
            for i in range(1, 4):
                consumer_name = f"consumer{i}"
                count = len([m for m in received_msgs if m.get('consumer') == consumer_name])
                total_consumer_msgs += count
                with consumer_cols[i-1]:
                    st.metric(f"Consumer {i}", count)

            # Total de mensagens recebidas por consumidor
            st.markdown(f"**Total Messages Received by All Consumers: {total_consumer_msgs}**")


        # Anomalies Section
        st.markdown("---")
        col_anomalies, col_recent = st.columns(2)

        with col_anomalies:
            st.subheader("⚠️ Detected Anomalies")

            # Path to persistent state file for anomalies
            state_file = os.path.join(self.log_service.logs_dir, 'anomalies_state.json')

            def load_anomaly_state(path):
                default = ({'critical': 0, 'high': 0, 'medium': 0, 'low': 0}, set())
                try:
                    if os.path.exists(path):
                        with open(path, 'r') as fh:
                            data = json.load(fh)
                        counts = data.get('counts', default[0])
                        processed = set(data.get('processed', []))
                        # ensure keys exist
                        for k in ['critical', 'high', 'medium', 'low']:
                            counts.setdefault(k, 0)
                        return counts, processed
                except Exception:
                    # if any problem reading state, return defaults
                    return default
                return default

            def save_anomaly_state(path, counts, processed_set):
                # write atomically
                tmp_fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(path))
                try:
                    with os.fdopen(tmp_fd, 'w') as fh:
                        json.dump({'counts': counts, 'processed': list(processed_set)}, fh)
                    os.replace(tmp_path, path)
                except Exception:
                    # best-effort: cleanup if write failed
                    try:
                        if os.path.exists(tmp_path):
                            os.remove(tmp_path)
                    except Exception:
                        pass

            # Load persisted state once into session_state (if not present)
            if 'cumulative_anomaly_counts' not in st.session_state or 'processed_anomalies' not in st.session_state:
                counts, processed = load_anomaly_state(state_file)
                st.session_state.cumulative_anomaly_counts = counts
                st.session_state.processed_anomalies = processed

            if anomalies:
                # Add new anomalies to cumulative count
                new_event = False
                for anomaly in anomalies:
                    # Create unique identifier for anomaly (timestamp + message)
                    anomaly_id = f"{anomaly['timestamp']}_{anomaly['message'][:50]}"

                    # Only count if not already processed
                    if anomaly_id not in st.session_state.processed_anomalies:
                        severity = anomaly.get('severity', 'low')
                        # guard against unexpected severities
                        if severity not in st.session_state.cumulative_anomaly_counts:
                            severity = 'low'
                        st.session_state.cumulative_anomaly_counts[severity] += 1
                        st.session_state.processed_anomalies.add(anomaly_id)
                        new_event = True

                # persist if there were changes
                if new_event:
                    try:
                        save_anomaly_state(state_file, st.session_state.cumulative_anomaly_counts, st.session_state.processed_anomalies)
                    except Exception:
                        # don't block UI on persistence failures
                        pass

                # Display cumulative severity metrics
                metric_cols = st.columns(4)
                with metric_cols[0]:
                    st.metric("🔴 Critical", st.session_state.cumulative_anomaly_counts['critical'])
                with metric_cols[1]:
                    st.metric("🟠 High", st.session_state.cumulative_anomaly_counts['high'])
                with metric_cols[2]:
                    st.metric("🟡 Medium", st.session_state.cumulative_anomaly_counts['medium'])
                with metric_cols[3]:
                    st.metric("🔵 Low", st.session_state.cumulative_anomaly_counts['low'])

                st.markdown("**Recent Anomalies:**")

                # Display recent anomalies (last 10)
                for i, anomaly in enumerate(anomalies[:10]):
                    severity_emoji = {
                        'critical': '🔴',
                        'high': '🟠',
                        'medium': '🟡',
                        'low': '🔵'
                    }

                    emoji = severity_emoji.get(anomaly.get('severity', 'low'), '⚪')

                    with st.expander(f"{emoji} {anomaly['type'].replace('_', ' ').title()} - {anomaly['timestamp']}"):
                        if anomaly.get('machine_id') and anomaly['machine_id'] != 'Unknown':
                            st.text(f"🏭 Machine: {anomaly['machine_id']}")
                        if anomaly.get('sector') and anomaly['sector'] != 'Unknown':
                            st.text(f"📍 Sector: {anomaly['sector']}")
                        if anomaly.get('sensor_value'):
                            st.text(f"📊 Value: {anomaly['sensor_value']}")
                        st.text(f"⚠️ Severity: {anomaly.get('severity', 'low').upper()}")
                        st.code(anomaly['message'], language='text')
            else:
                st.success("✅ No anomalies detected")

        with col_recent:
            st.subheader("📋 Recent Activity")
            # Combine all activities
            all_activities = []

            # Add producer activities
            for msg in sensors_msgs[-5:]:
                all_activities.append({
                    'timestamp': msg['timestamp'],
                    'type': f"📤 Message Sent by {msg['sensor']}",
                    'details': f"Partition {msg['partition']}, Offset {msg['offset']}"
                })

            # Add consumer activities
            for msg in received_msgs[-5:]:
                all_activities.append({
                    'timestamp': msg['timestamp'],
                    'type': f"📥 Message Received by {msg['consumer']}",
                    'details': f"Machine {msg['machine_id']}"
                })

            # Sort by timestamp
            all_activities.sort(key=lambda x: x['timestamp'], reverse=True)

            if all_activities:
                for activity in all_activities[:10]:
                    st.text(f"{activity['type']}")
                    st.caption(f"⏰ {activity['timestamp']} - {activity['details']}")
                    st.markdown("---")
            else:
                st.info("No recent activity found")


def main():
    """Main Streamlit app function"""
    # Auto-refresh every 5 seconds
    if 'auto_refresh' not in st.session_state:
        st.session_state.auto_refresh = True

    # Sidebar controls
    st.sidebar.title("Dashboard Controls")
    auto_refresh = st.sidebar.checkbox("Auto-refresh (5s)", value=st.session_state.auto_refresh)
    st.session_state.auto_refresh = auto_refresh

    if st.sidebar.button("Refresh Now"):
        st.rerun()

    # Cria o dashboard
    try:
        analyzer = LogAnalyzer()
        analyzer.display_streamlit_dashboard()

        # Auto-refresh
        if auto_refresh:
            time.sleep(5)
            st.rerun()

    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")
        st.info("Make sure the log service and files are available.")

if __name__ == "__main__":
    main()