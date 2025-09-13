# collector_iothub_to_servicebus.py
import os, json, time, re, sys
from pathlib import Path
from dotenv import load_dotenv
from azure.eventhub import EventHubConsumerClient
from azure.servicebus import ServiceBusClient, ServiceBusMessage

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

EH_CONN = os.getenv("EVENTHUB_CONN_STR")
EH_NAME = os.getenv("EVENTHUB_NAME")  # Only used if no EntityPath in EH_CONN
SB_CONN = os.getenv("SERVICE_BUS_CONN_STR")
SB_TOPIC = os.getenv("SERVICE_BUS_TOPIC", "dk-weather-stock-reports")

# --- Validate environment variables ---
if not EH_CONN:
    sys.exit("❌ Missing EVENTHUB_CONN_STR in .env")
if not SB_CONN:
    sys.exit("❌ Missing SERVICE_BUS_CONN_STR in .env")
if not SB_TOPIC:
    sys.exit("❌ Missing SERVICE_BUS_TOPIC in .env")

# --- Parse EntityPath if present ---
m = re.search(r"(?:^|;)EntityPath=([^;]+)", EH_CONN or "")
if m:
    effective_eh_name = None
    print(f"ℹ️ Using EntityPath from connection string: {m.group(1)}")
else:
    if not EH_NAME:
        sys.exit("❌ EVENTHUB_NAME is required if EntityPath is missing in EVENTHUB_CONN_STR")
    effective_eh_name = EH_NAME
    print(f"ℹ️ Using event hub name from EVENTHUB_NAME: {EH_NAME}")

# --- Buffers to merge messages ---
buffer = {"weather": None, "finance": None}

def try_emit_combined():
    """Send combined weather+finance once both are present"""
    if buffer["weather"] and buffer["finance"]:
        combined = {
            "weather": buffer["weather"],
            "finance": buffer["finance"],
            "combined_ts": int(time.time())
        }
        print("➡️  Publishing combined report to Service Bus:", combined)
        with ServiceBusClient.from_connection_string(SB_CONN) as sb:
            with sb.get_topic_sender(topic_name=SB_TOPIC) as sender:
                sender.send_messages(ServiceBusMessage(json.dumps(combined)))
        print("✅ combined report sent")
        buffer["weather"] = None
        buffer["finance"] = None

def on_event(partition_context, event):
    body = event.body_as_str()
    try:
        data = json.loads(body)
    except Exception:
        print("Ignoring non-JSON message:", body[:200])
        partition_context.update_checkpoint(event)
        return

    t = data.get("type")
    if t == "weather":
        buffer["weather"] = data
        print("📥 weather msg from IoT Hub:", data)
    elif t == "finance":
        buffer["finance"] = data
        print("📥 finance msg from IoT Hub:", data)
    else:
        print("Ignoring unknown type:", data)

    try_emit_combined()
    partition_context.update_checkpoint(event)

def main():
    print("▶️  Collector listening on IoT Hub built-in endpoint… (Ctrl+C to stop)")
    client = EventHubConsumerClient.from_connection_string(
        conn_str=EH_CONN,
        consumer_group="$Default",
        eventhub_name=effective_eh_name,  # only needed if EntityPath missing
    )
    with client:
        client.receive(on_event=on_event, starting_position="-1")

if __name__ == "__main__":
    main()
