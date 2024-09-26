import time
import datetime
import logging
from config_execution_api import (
    session,
    TICKER_1,
    TICKER_2,
    TIMEFRAME,
    KLINE_LIMIT
)
from func_calculations import extract_close_prices

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get trade liquidity for ticker
def get_ticker_trade_liquidity(ticker):
    try:
        # Get trades history
        trades = session.get_public_trade_history(
            category="linear",
            symbol=ticker,
            limit=50
        )

        # Проверяем успешность ответа
        if trades["retCode"] == 0:
            quantity_list = []
        
            # Получаем список объёмов сделок для расчёта средней ликвидности
            for trade in trades["result"]["list"]:
                quantity_list.append(float(trade["size"]))

            # Возвращаем среднюю ликвидность и последнюю цену сделки
            if quantity_list:
                avg_liq = sum(quantity_list) / len(quantity_list)
                last_trade_price = float(trades["result"]["list"][0]["price"])
                logging.info(f"Средняя ликвидность для {ticker}: {avg_liq}, Последняя цена: {last_trade_price}")
                return avg_liq, last_trade_price
            else:
                logging.warning(f"Нет доступных данных о торгах для {ticker}.")
                return 0, 0
        else:
            logging.error(f"Ошибка при получении торговых записей для {ticker}: {trades['retMsg']}")
            return 0, 0
    except Exception as e:
        logging.error(f"Исключение при получении ликвидности для {ticker}: {e}")
        return 0, 0

# Get start times
def get_timestamps():
    time_start_date = 0
    time_next_date = 0
    now = datetime.datetime.now()
    if TIMEFRAME == 60:
        time_start_date = now - datetime.timedelta(hours=KLINE_LIMIT)
        time_next_date = now + datetime.timedelta(seconds=30)
    if TIMEFRAME == "D":
        time_start_date = now - datetime.timedelta(days=KLINE_LIMIT)
        time_next_date = now + datetime.timedelta(minutes=1)
    time_start_seconds = int(time_start_date.timestamp())
    time_now_seconds = int(now.timestamp())
    time_next_seconds = int(time_next_date.timestamp())
    return (time_start_seconds, time_now_seconds, time_next_seconds)

# Get historical prices (klines)
def get_price_klines(ticker):

    # Get prices
    time_start_seconds, _, _ = get_timestamps()
    prices = session.get_mark_price_kline(
        category='linear',
        symbol=ticker,
        interval=TIMEFRAME,
        start=time_start_seconds,
        end=datetime.datetime.now().timestamp(), 
        limit=KLINE_LIMIT
        )

    # Manage API calls
    time.sleep(0.1)

    # Return prices output
    if len(prices['result']['list']) != KLINE_LIMIT:
        return []
    return prices['result']['list']

# Get latest klines
def get_latest_klines():
    series_1 = []
    series_2 = []
    prices_1 = get_price_klines(TICKER_1)
    prices_2 = get_price_klines(TICKER_2)
    if len(prices_1) > 0:
        series_1 = extract_close_prices(prices_1)
    if len(prices_2) > 0:
        series_2 = extract_close_prices(prices_2)
    return (series_1, series_2)
