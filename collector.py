# collector.py
import os, json
from pathlib import Path
from dotenv import load_dotenv
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from weather_now import get_weather
from finance_now import get_quote

# Load .env from project root
ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

SERVICE_BUS_CONN_STR = os.getenv("SERVICE_BUS_CONN_STR")
SERVICE_BUS_TOPIC = os.getenv("SERVICE_BUS_TOPIC")
YF_TICKER = (os.getenv("YF_TICKER") or "MSFT").strip().upper()

if not SERVICE_BUS_CONN_STR or not SERVICE_BUS_TOPIC:
    raise RuntimeError("Missing SERVICE_BUS_* settings in .env")

def send_combined_to_sb(weather, finance):
    with ServiceBusClient.from_connection_string(SERVICE_BUS_CONN_STR) as client:
        sender = client.get_topic_sender(topic_name=SERVICE_BUS_TOPIC)
        with sender:
            combined = {"weather": weather, "finance": finance}
            sender.send_messages(ServiceBusMessage(json.dumps(combined)))
    print(f"✅ Sent combined report to topic '{SERVICE_BUS_TOPIC}'")

def main():
    print("🔍 Fetching weather and finance data...")
    weather = get_weather()
    finance = get_quote(YF_TICKER)
    print("🌦️ Weather:", weather)
    print("💹 Finance:", finance)
    send_combined_to_sb(weather, finance)

if __name__ == "__main__":
    main()
