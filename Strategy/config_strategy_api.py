"""
API Documentation: https://bybit-exchange.github.io/docs/v5/intro
"""

import os
from pybit.unified_trading import HTTP
from dotenv import load_dotenv


load_dotenv() 

# CONFIG
MODE = "test"
TIMEFRAME = 60
KLINE_LIMIT = 200
Z_SCORE_WINDOW = 21

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


session = HTTP(
    testnet=True if MODE == "test" else False,
    api_key=API_KEY,
    api_secret=API_SECRET,
)

# print(session.get_wallet_balance(
#     accountType="UNIFIED",
# ))