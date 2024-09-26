import logging
from time import sleep

from config_execution_api import ws, TICKER_1, TICKER_2
from func_calculations import get_trade_details
from func_price_calls import get_latest_klines
from func_stats import calculate_metrics


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Функция для получения последнего z-score
def get_latest_zscore():

    # Переменные для хранения последней цены
    mid_price_1 = None
    mid_price_2 = None

    # Callback-функция для обработки данных ордербука
    def handle_message(message):
        nonlocal mid_price_1, mid_price_2  # Доступ к переменным из внешней области видимости
        if message['topic'] == f'orderbook.50.{TICKER_1}':
            mid_price_1, _, _ = get_trade_details(message)
            logging.info(f"Получена средняя цена для {TICKER_1}: {mid_price_1}")
        elif message['topic'] == f'orderbook.50.{TICKER_2}':  # Предположим, что вторая пара — {TICKER_2}
            mid_price_2, _, _ = get_trade_details(message)
            logging.info(f"Получена средняя цена для {TICKER_2}: {mid_price_2}")

    # Подписка на потоки ордербуков для двух активов (например, {TICKER_1} и {TICKER_2})
    ws.orderbook_stream(
        depth=50,
        symbol=TICKER_1,
        callback=handle_message
    )
    
    ws.orderbook_stream(
        depth=50,
        symbol=TICKER_2,
        callback=handle_message
    )

    # Ожидание получения данных через WebSocket
    while mid_price_1 is None or mid_price_2 is None:
        sleep(1)

    # Получаем исторические данные по ценам (Klines)
    series_1, series_2 = get_latest_klines()
    # print(series_1)

    # Если история цен доступна
    if len(series_1) > 0 and len(series_2) > 0:

        # Обновляем последнюю свечу последней ценой из ордербука
        series_1 = series_1[:-1]
        series_2 = series_2[:-1]
        series_1.append(mid_price_1)
        series_2.append(mid_price_2)

        # Рассчитываем z-score
        _, zscore_list = calculate_metrics(series_1, series_2)
        zscore = zscore_list[-1]
        signal_sign_positive = zscore > 0

        logging.info(f"Z-score: {zscore}, Положительный сигнал: {signal_sign_positive}")

        # Возвращаем z-score и сигнал
        return zscore, signal_sign_positive

    # Если данные отсутствуют, возвращаем None
    logging.warning("Недостаточно данных для расчёта Z-score.")
    return None

# Пример вызова функции
# get_latest_zscore()
    
 