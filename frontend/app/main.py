import os
import time
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
    def __init__(self, logs_dir=None):
        if logs_dir is None:
            # Auto-detect the correct logs directory based on environment
            if os.path.exists('/app/logs'):
                # Running inside Docker container
                logs_dir = '/app/logs'
            else:
                # Running in development environment
                logs_dir = '/workspaces/INF1304-T1/logs'
        self.log_service = LogService(logs_dir)

    def read_sensors_logs(self):
        """Lê e analisa logs dos sensores"""
        return self.log_service.get_sensors_messages()

    def read_consumers_logs(self):
        """Lê e analisa logs dos consumidores"""
        return self.log_service.get_consumers_messages()

    def get_kafka_status(self):
        """Verifica status dos brokers Kafka"""
        return self.log_service.get_kafka_broker_status()

    def get_services_status(self):
        """Verifica status dos sensores e consumidores"""
        return self.log_service.get_services_status()

    def get_anomaly_messages(self):
        """Retorna mensagens de anomalia detectadas"""
        return self.log_service.get_anomaly_messages()

    def display_streamlit_dashboard(self):
        """Exibe um dashboard Streamlit com informações dos logs"""

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
            # Separate sensors and consumers for display
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
            # Messages per Sensor with better visualization
            st.markdown("**Messages per Sensor**")
            sensor_cols = st.columns(3)
            total_sensor_msgs = 0
            for i in range(1, 4):
                sensor_name = f"sensor{i}"
                count = len([m for m in sensors_msgs if m.get('sensor') == sensor_name])
                total_sensor_msgs += count
                with sensor_cols[i-1]:
                    st.metric(f"Sensor {i}", count)

            # Total messages sent by all sensors
            st.markdown(f"**Total Messages Sent by All Sensors: {total_sensor_msgs}**")

            # Messages per Consumer with better visualization
            st.markdown("**Messages per Consumer**")
            consumer_cols = st.columns(3)
            total_consumer_msgs = 0
            for i in range(1, 4):
                consumer_name = f"consumer{i}"
                count = len([m for m in received_msgs if m.get('consumer') == consumer_name])
                total_consumer_msgs += count
                with consumer_cols[i-1]:
                    st.metric(f"Consumer {i}", count)

            # Total messages received by all consumers
            st.markdown(f"**Total Messages Received by All Consumers: {total_consumer_msgs}**")


        # Anomalies Section - Full width
        st.markdown("---")
        col_anomalies, col_recent = st.columns(2)

        with col_anomalies:
            st.subheader("⚠️ Detected Anomalies")
            if anomalies:
                # Show anomaly count by severity
                severity_counts = {}
                for anomaly in anomalies:
                    severity = anomaly['severity']
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1

                # Display severity metrics
                metric_cols = st.columns(4)
                with metric_cols[0]:
                    st.metric("🔴 Critical", severity_counts.get('critical', 0))
                with metric_cols[1]:
                    st.metric("🟠 High", severity_counts.get('high', 0))
                with metric_cols[2]:
                    st.metric("🟡 Medium", severity_counts.get('medium', 0))
                with metric_cols[3]:
                    st.metric("🔵 Low", severity_counts.get('low', 0))

                st.markdown("**Recent Anomalies:**")

                # Display recent anomalies (last 10)
                for i, anomaly in enumerate(anomalies[:10]):
                    severity_emoji = {
                        'critical': '🔴',
                        'high': '🟠',
                        'medium': '🟡',
                        'low': '🔵'
                    }

                    emoji = severity_emoji.get(anomaly['severity'], '⚪')

                    with st.expander(f"{emoji} {anomaly['type'].replace('_', ' ').title()} - {anomaly['timestamp']}"):
                        if anomaly.get('machine_id') and anomaly['machine_id'] != 'Unknown':
                            st.text(f"🏭 Machine: {anomaly['machine_id']}")
                        if anomaly.get('sector') and anomaly['sector'] != 'Unknown':
                            st.text(f"📍 Sector: {anomaly['sector']}")
                        if anomaly.get('sensor_value'):
                            st.text(f"📊 Value: {anomaly['sensor_value']}")
                        st.text(f"⚠️ Severity: {anomaly['severity'].upper()}")
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

    # Create analyzer and display dashboard
    try:
        analyzer = LogAnalyzer()
        analyzer.display_streamlit_dashboard()

        # Auto-refresh functionality
        if auto_refresh:
            time.sleep(5)
            st.rerun()

    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")
        st.info("Make sure the log service and files are available.")

if __name__ == "__main__":
    main()