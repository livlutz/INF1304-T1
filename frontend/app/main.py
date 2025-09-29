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
    def __init__(self, logs_dir="/workspaces/INF1304-T1/logs"):
        self.log_service = LogService(logs_dir)

    def read_producer_logs(self):
        """Lê e analisa logs do producer"""
        return self.log_service.get_producer_messages()

    def read_consumer_logs(self):
        """Lê e analisa logs do consumer"""
        return self.log_service.get_consumer_messages()

    def get_kafka_status(self):
        """Verifica status dos brokers Kafka"""
        return self.log_service.get_kafka_broker_status()

    def get_anomaly_messages(self):
        """Retorna mensagens de anomalia detectadas"""
        return self.log_service.get_anomaly_messages()

    # ...existing code...

    def display_streamlit_dashboard(self):
        """Exibe um dashboard Streamlit com informações dos logs"""

        # Main title
        st.title("📊 Kafka Monitoring Dashboard")
        st.markdown("---")

        # Get data
        kafka_status = self.get_kafka_status()
        producer_msgs = self.read_producer_logs()
        consumer_msgs = self.read_consumer_logs()
        received_msgs = [m for m in consumer_msgs if m['type'] == 'received']
        anomalies = self.get_anomaly_messages()

        # Create columns for layout
        col1, col2, col3 = st.columns(3)

        # Kafka Brokers Status
        with col1:
            st.subheader("🔧 Kafka Brokers Status")
            for broker, status in kafka_status.items():
                if status == "RUNNING":
                    st.success(f"● {broker}: {status}")
                elif status == "ERROR":
                    st.error(f"● {broker}: {status}")
                else:
                    st.warning(f"● {broker}: {status}")

        # Producer Stats
        with col2:
            st.subheader("📤 Producer Stats")
            st.metric("Total Messages Sent", len(producer_msgs))
            if producer_msgs:
                latest = producer_msgs[-1]
                st.text(f"Last message: {latest['timestamp']}")
                st.text(f"Partition: {latest['partition']}")

        # Consumer Stats
        with col3:
            st.subheader("📥 Consumer Stats")
            st.metric("Total Messages Received", len(received_msgs))
            if received_msgs:
                latest = received_msgs[-1]
                st.text(f"Last message: {latest['timestamp']}")

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
                        st.text(f"Source: {anomaly['source']}")
                        st.text(f"Severity: {anomaly['severity'].upper()}")
                        st.text(f"Line: {anomaly.get('line', 'N/A')}")
                        st.code(anomaly['message'], language='text')
            else:
                st.success("✅ No anomalies detected")

        with col_recent:
            st.subheader("📋 Recent Activity")
            # Combine all activities
            all_activities = []

            # Add producer activities
            for msg in producer_msgs[-5:]:
                all_activities.append({
                    'timestamp': msg['timestamp'],
                    'type': '📤 Message Sent',
                    'details': f"Partition {msg['partition']}, Offset {msg['offset']}"
                })

            # Add consumer activities
            for msg in received_msgs[-5:]:
                all_activities.append({
                    'timestamp': msg['timestamp'],
                    'type': '📥 Message Received',
                    'details': f"Consumer activity"
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

# ...existing code...


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