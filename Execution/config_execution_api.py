"""    API Documentation: https://bybit-exchange.github.io/docs/v5/intro    """

# API Imports
import os
from pybit.unified_trading import HTTP

# CONFIG VARIABLES
MODE = "test"
TICKER_1 = "AXSUSDT"
TICKER_2 = "ENAUSDT"
SIGNAL_POSITIVE_TICKER = TICKER_2
SIGNAL_NEGATIVE_TICKER = TICKER_1
ROUNDING_TICKER_1 = 3
ROUNDING_TICKER_2 = 4
QUANTITY_ROUNDING_TICKER_1 = 0
QUANTITY_ROUNDING_TICKER_2 = 0

LIMIT_ORDER_BASIS = True  # Will ensure positions (except for close) will be placed on limit basis

TRADEABLE_CAPITAL_USDT = 2000  # total tradeable capital to be split between both pairs
STOP_LOSS_FAIL_SAFE = 0.15  # stop loss at market order in case of drastic event
SIGNAL_TRIGGER_THRESH = 0.8  # Z-Score threshold which determines trade (mast be above zero)

TIMEFRAME = 60  # make sure matches your strategy
KLINE_LIMIT = 200  # make sure matches your strategy
Z_SCORE_WINDOW = 21  # make sure matches your strategy

# LIVE API
API_KEY_LIVE = os.getenv("API_kEY_BYBIT")
API_SECRET_LIVE = os.getenv("API_SECRET_BYBIT")

# TESTNET API
API_KEY_TEST = os.getenv("API_kEY_BYBIT_TESTNET")
API_SECRET_TEST = os.getenv("API_SECRET_BYBIT_TESTNET")

# SELECTED API
API_KEY = API_KEY_TEST if MODE == "test" else API_KEY_LIVE
API_SECRET = API_SECRET_TEST if MODE == "test" else API_SECRET_LIVE

# SELECTED URL
API_URL = "https://api-testnet.bybit.com" if MODE == "test" else "https://api.bybit.com"
WS_PUBLIC_URL = "wss://stream-testnet.bybit.com/v5/public/linear" if MODE == "test" else "wss://stream.bybit.com/v5/public/linear"


session = HTTP(
    testnet=True if MODE == "test" else False,
    api_key=API_KEY,
    api_secret=API_SECRET,
)

from pybit.unified_trading import WebSocket
from time import sleep

ws = WebSocket(
    testnet=True,
    channel_type="linear",
)
# def handle_message(message):
#     print(message)
# ws.orderbook_stream(
#     depth=50,  # Можно выбрать 1, 50, 200 или 500
#     symbol=[TICKER_1, TICKER_2],
#     callback=handle_message
# )
# while True:
#     sleep(1)