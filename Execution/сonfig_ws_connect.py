from config_execution_api import (
    WS_PUBLIC_URL,
    TICKER_1,
    TICKER_2
)

from pybit.unified_trading import WebSocket
from time import sleep

ws = WebSocket(
    testnet=True,
    channel_type="linear",
)
def handle_message(message):
    print(message)
ws.orderbook_stream(
    depth=50,  # Можно выбрать 1, 50, 200 или 500
    symbol=[TICKER_1, TICKER_2],
    callback=handle_message
)
while True:
    sleep(1)