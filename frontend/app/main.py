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
    def __init__(self, logs_dir="/app/logs"):
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

        # Recent Activity Section
        st.markdown("---")
        st.subheader("📋 Recent Activity")

        # Combine and sort recent messages
        all_recent = (producer_msgs[-3:] + received_msgs[-3:])
        all_recent.sort(key=lambda x: x['timestamp'], reverse=True)

        if all_recent:
            for msg in all_recent[:5]:
                if 'status' in msg:  # Producer message
                    st.success(f"[SENT] {msg['timestamp']} - Partition {msg['partition']}")
                else:  # Consumer message
                    st.info(f"[RECV] {msg['timestamp']} - Message processed")
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