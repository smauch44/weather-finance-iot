# receive_once.py
import os, json
from pathlib import Path
from dotenv import load_dotenv
from azure.servicebus import ServiceBusClient

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

SB_CONN = os.getenv("SERVICE_BUS_CONN_STR")
SB_TOPIC = os.getenv("SERVICE_BUS_TOPIC", "dk-weather-stock-reports")
SB_SUB   = os.getenv("SERVICE_BUS_SUBSCRIPTION", "dk-weather-stock-sub")

if not SB_CONN:
    raise RuntimeError("Missing SERVICE_BUS_CONN_STR in .env")

with ServiceBusClient.from_connection_string(SB_CONN) as sb:
    receiver = sb.get_subscription_receiver(
        topic_name=SB_TOPIC,
        subscription_name=SB_SUB,
        max_wait_time=15  
    )
    with receiver:
        print(f"Listening on {SB_TOPIC}/{SB_SUB}…")
        for msg in receiver:
            body = str(msg)
            try:
                obj = json.loads(body)
                if isinstance(obj, dict) and "weather" in obj and "finance" in obj:
                    w, f = obj["weather"], obj["finance"]
                    print("Combined report")
                    print(f"  City: {w['city']}, {w['temperature_c']}°C, {w['condition']}, RH {w['humidity']}%, wind {w['wind_ms']} m/s")
                    print(f"  Ticker: {f['symbol']} @ {f['price']} {f['currency']} ({f['exchange']})")
                else:
                    print("received JSON:", obj)
            except Exception:
                print("received text:", body)
            receiver.complete_message(msg)
            break

print("receive_once done")

