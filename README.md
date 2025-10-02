IoT Weather + Finance Pipeline

This project collects weather and finance data, sends them through IoT Hub
devices, consumes the messages from the IoT Hub’s Event Hub-compatible endpoint,
combines them, and publishes the combined result to an Azure Service Bus topic.

1.) Project Structure
assignment/
│
├── __pycache__/                         # Compiled Python cache files
│
├── .env                                 # Environment variables (not checked in)
├── Documentation.docx                   # Project documentation (optional)
│
├── iot_weather_proxy.py                 # Sends live weather data to IoT Hub (device: weather-proxy)
├── iot_finance_proxy.py                 # Sends live stock price to IoT Hub (device: finance-proxy)
│
├── collector_iothub_to_servicebus.py    # Core collector: combines weather + finance from IoT Hub → sends to Service Bus
├── collector.py                         # (Optional/legacy) collector prototype script
│
├── receive_once.py                      # Reads and prints a single message from Service Bus topic/subscription
│
├── finance_now.py                       # Prints current stock price to console (for quick testing)
├── finance_send_to_sb.py                # Sends current stock price directly to Service Bus (bypasses IoT Hub)
│
├── weather_now.py                       # Prints current weather to console (for quick testing)
├── weather_send_to_sb.py                # Sends current weather directly to Service Bus (bypasses IoT Hub)
│
└── readme.md                            


2.) Prerequisites
- IoT Hub (Standard tier)
- Two IoT Devices:
    weather-proxy
    finance-proxy
- Azure Service Bus Namespace:
    Topic: dk-weather-stock-reports
    Subscription: dk-weather-stock-sub
- Python 3.10+ with dependencies:
pip install python-dotenv azure-iot-device azure-eventhub azure-servicebus yfinance requests

3.) Environment Configuration

OPENWEATHER_API_KEY=YOUR_OPENWEATHER_KEY
YF_TICKER=MSFT

IOTHUB_DEVICE_CONN_STR_WEATHER=HostName=rg-jwh-course604.azure-devices.net;DeviceId=weather-proxy;SharedAccessKey=YOUR_WEATHER_DEVICE_PRIMARY_KEY
IOTHUB_DEVICE_CONN_STR_FINANCE=HostName=rg-jwh-course604.azure-devices.net;DeviceId=finance-proxy;SharedAccessKey=YOUR_FINANCE_DEVICE_PRIMARY_KEY

EVENTHUB_CONN_STR=Endpoint=sb://iothub-ns-rg-jwh-cours-XXXXXXXXX.servicebus.windows.net/;SharedAccessKeyName=iothubowner;SharedAccessKey=YOUR_IOTHUBOWNER_PRIMARY_KEY;EntityPath=rg-jwh-course604

SERVICE_BUS_CONN_STR=Endpoint=sb://dev-jhu-aiclass-sb-testbus.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=YOUR_SB_ROOTMANAGE_KEY
SERVICE_BUS_TOPIC=dk-weather-stock-reports
SERVICE_BUS_SUBSCRIPTION=dk-weather-stock-sub

4.) Run Weather and Finance KPI 
python iot_weather_proxy.py
python iot_finance_proxy.py

✅ weather proxy → IoT Hub sent
✅ finance proxy → IoT Hub sent

5.) Run Collector
This script reads events from the IoT Hub’s Event Hub-compatible endpoint,
buffers one weather and one finance message, then publishes them as a combined
report to the Service Bus topic.

python collector_iothub_to_servicebus.py
📥 weather msg from IoT Hub: {...}
📥 finance msg from IoT Hub: {...}
➡️  Publishing combined report to Service Bus: {...}
✅ combined report sent

6.) Verify Service Bus
python receive_once.py
received JSON: { "weather": {...}, "finance": {...}, "combined_ts": ... }
receive_once done

7.) Pipeline
weather-proxy  ─┐
                │            ┌────────────┐
finance-proxy ──┼─> IoT Hub ─> Event Hub  │
                │            └────────────┘
                │                     │
                └────> collector_iothub_to_servicebus.py
                                     │
                         Azure Service Bus Topic

Output:
(base) stefanmauch@Stefans-MacBook-Pro assignment % python collector_iothub_to_servicebus.py
ℹ️ Using EntityPath from connection string: rg-jwh-course604
▶️  Collector listening on IoT Hub built-in endpoint… (Ctrl+C to stop)
📥 finance msg from IoT Hub: {'type': 'finance', 'symbol': 'MSFT', 'price': 509.8999938964844, 'currency': 'USD', 'exchange': 'NMS', 'source': 'yahoo-finance'}
📥 weather msg from IoT Hub: {'type': 'weather', 'city': 'Berlin', 'city_id': 2950159, 'temperature_c': 15.04, 'feels_like_c': 14.61, 'condition': 'clear sky', 'humidity': 77, 'wind_ms': 4.12, 'source': 'openweathermap'}
➡️  Publishing combined report to Service Bus: {'weather': {'type': 'weather', 'city': 'Berlin', 'city_id': 2950159, 'temperature_c': 15.04, 'feels_like_c': 14.61, 'condition': 'clear sky', 'humidity': 77, 'wind_ms': 4.12, 'source': 'openweathermap'}, 'finance': {'type': 'finance', 'symbol': 'MSFT', 'price': 509.8999938964844, 'currency': 'USD', 'exchange': 'NMS', 'source': 'yahoo-finance'}, 'combined_ts': 1757798706}
✅ combined report sent
📥 weather msg from IoT Hub: {'type': 'weather', 'city': 'Berlin', 'city_id': 2950159, 'temperature_c': 15.04, 'feels_like_c': 14.61, 'condition': 'clear sky', 'humidity': 77, 'wind_ms': 4.12, 'source': 'openweathermap'}
