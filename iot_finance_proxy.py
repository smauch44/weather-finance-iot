import os, json
from pathlib import Path
from dotenv import load_dotenv
from azure.iot.device import IoTHubDeviceClient, Message
import yfinance as yf

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

DEVICE_CONN = os.getenv("IOTHUB_DEVICE_CONN_STR_FINANCE")
TICKER = (os.getenv("YF_TICKER") or "MSFT").strip().upper()

if not DEVICE_CONN:
    raise RuntimeError("Missing IOTHUB_DEVICE_CONN_STR_FINANCE")

def main():
    t = yf.Ticker(TICKER)
    fi = t.fast_info
    price = fi.last_price
    ccy = fi.currency or "USD"
    exch = fi.exchange or "NMS"
    if price is None:
        raise RuntimeError("Unable to fetch price (try again in a moment)")

    payload = {
        "type": "finance",
        "symbol": TICKER,
        "price": float(price),
        "currency": ccy,
        "exchange": exch,
        "source": "yahoo-finance",
    }
    print("Sending to IoT Hub:", payload)
    client = IoTHubDeviceClient.create_from_connection_string(DEVICE_CONN)
    client.connect()
    client.send_message(Message(json.dumps(payload)))
    client.disconnect()
    print("✅ finance proxy → IoT Hub sent")

if __name__ == "__main__":
    main()

