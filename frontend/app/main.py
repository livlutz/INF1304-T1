import os
import time
from colorama import init, Fore
from services.log_service import LogService

init(autoreset=True)

# TODO: fazer uma pagina mais bonita com html e css

class LogAnalyzer:
    def __init__(self, logs_dir="../../logs"):
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

    def display_dashboard(self):
        """Exibe um dashboard com informações dos logs"""
        os.system('clear' if os.name == 'posix' else 'cls')

        print(Fore.CYAN + "=" * 60)
        print(Fore.CYAN + "    KAFKA MONITORING DASHBOARD")
        print(Fore.CYAN + "=" * 60)
        print()

        # Status dos Kafka brokers
        print(Fore.YELLOW + "📊 KAFKA BROKERS STATUS:")
        kafka_status = self.get_kafka_status()
        for broker, status in kafka_status.items():
            color = Fore.GREEN if status == "RUNNING" else Fore.RED if status == "ERROR" else Fore.YELLOW
            print(f"  {color}● {broker}: {status}")
        print()

        # Producer stats
        producer_msgs = self.read_producer_logs()
        print(Fore.YELLOW + f"📤 PRODUCER STATS:")
        print(f"  Total messages sent: {Fore.GREEN}{len(producer_msgs)}")
        if producer_msgs:
            latest = producer_msgs[-1]
            print(f"  Last message: {latest['timestamp']} (partition {latest['partition']})")
        print()

        # Consumer stats
        consumer_msgs = self.read_consumer_logs()
        received_msgs = [m for m in consumer_msgs if m['type'] == 'received']
        print(Fore.YELLOW + f"📥 CONSUMER STATS:")
        print(f"  Total messages received: {Fore.GREEN}{len(received_msgs)}")
        if received_msgs:
            latest = received_msgs[-1]
            print(f"  Last message: {latest['timestamp']}")
        print()

        # Recent activity
        print(Fore.YELLOW + "📋 RECENT ACTIVITY (last 5 messages):")
        all_recent = (producer_msgs[-3:] + received_msgs[-3:])
        all_recent.sort(key=lambda x: x['timestamp'], reverse=True)

        for msg in all_recent[:5]:
            if 'status' in msg:  # Producer message
                print(f"  {Fore.GREEN}[SENT] {msg['timestamp']} - Partition {msg['partition']}")
            else:  # Consumer message
                print(f"  {Fore.CYAN}[RECV] {msg['timestamp']} - Message processed")

        print()
        print(Fore.MAGENTA + "Press Ctrl+C to exit...")

def main():
    analyzer = LogAnalyzer()

    try:
        while True:
            analyzer.display_dashboard()
            time.sleep(5)  # Refresh every 5 seconds
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n\nDashboard fechado. Até logo!")

if __name__ == "__main__":
    main()