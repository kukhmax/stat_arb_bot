"""
    interval: 60, "D"
    from: integer from timestamp in seconds
    limit: max size of 200
"""

import datetime
import time
from config_strategy_api import session, TIMEFRAME, KLINE_LIMIT

# Get start times
time_start_date = 0
if TIMEFRAME == 60:
    time_start_date = datetime.datetime.now() - datetime.timedelta(hours=KLINE_LIMIT)
if TIMEFRAME == "D":
    time_start_date = datetime.datetime.now() - datetime.timedelta(days=KLINE_LIMIT)
time_start_seconds = int(time_start_date.timestamp())

# Get historical prices
def get_price_kline(symbol):
    prices = session.get_mark_price_kline(
        category='linear',
        symbol=symbol,
        interval=TIMEFRAME,
        start=time_start_seconds,
        end=datetime.datetime.now().timestamp(), 
        limit=KLINE_LIMIT
        )
    time.sleep(0.1)
    if len(prices['result']['list']) != KLINE_LIMIT:
        return []
    return prices