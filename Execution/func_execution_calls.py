import logging
import inspect
from config_execution_api import session, LIMIT_ORDER_BASIS
from func_calculations import get_trade_details

from pybit.unified_trading import WebSocket
from colorama import Fore, Style


# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Функция для получения текущей строки кода и названия функции для логов
def log_info(message):
    frame = inspect.currentframe().f_back
    logging.info(f"{message} | Function: {frame.f_code.co_name} | Line: {frame.f_lineno}")

def log_error(message):
    frame = inspect.currentframe().f_back
    logging.error(Fore.RED + f"{message} | Function: {frame.f_code.co_name} | Line: {frame.f_lineno}" + Style.RESET_ALL)


# Установка плеча
def set_leverage(ticker):
    try:
        # Устанавливаем плечо для позиции
        response = session.set_leverage(
            category="linear",
            symbol=ticker,
            buyLeverage="1",
            sellLeverage="1"
        )
        print(response)
        if response["retCode"] == 0:
            log_info(f"Плечо успешно установлено для {ticker}")
        else:
            log_error(f"Ошибка установки плеча для {ticker}: {response['retMsg']}")
    except Exception as e:
        log_error(f"Исключение при установке плеча для {ticker}: {e}")

# Размещение лимитного или рыночного ордера
def place_order(ticker, price, quantity, direction, stop_loss):
    # Определение стороны сделки
    side = "Buy" if direction == "Long" else "Sell"

    try:
        # Размещение лимитного ордера
        if LIMIT_ORDER_BASIS:
            order = session.place_order(
                category="linear", 
                symbol=ticker,
                side=side,
                orderType="Limit",
                qty=quantity,
                price=price,
                timeInForce="PostOnly",
                reduceOnly=False,
                closeOnTrigger=False,
                stopLoss=stop_loss
            )
        else:
            # Размещение рыночного ордера
            order = session.place_order(
                category="linear",
                symbol=ticker,
                side=side,
                orderType="Market",
                qty=quantity,
                timeInForce="GTC",
                reduceOnly=False,
                closeOnTrigger=False,
                stopLoss=stop_loss
            )

        # Проверка успешности размещения ордера
        if order["retCode"] == 0:
            log_info(Fore.YELLOW + f"Ордера на {side} {quantity} {ticker} успешно размещён." + Style.RESET_ALL)
            return order["result"]["orderId"]
        else:
            log_error(f"Ошибка размещения ордера по {ticker}: {order['retMsg']}")
            return 0
    except Exception as e:
        log_error(f"Исключение при размещении ордера по {ticker}: {e}")
        return 0
    
  
def initialise_order_execution(ticker, direction, capital):
    
    # Переменная для отслеживания, был ли размещён ордер
    order_id = False

    # Callback-функция для обработки потока ордербука
    def handle_message(message):
        nonlocal order_id  # Доступ к переменной из внешней области видимости

        # Проверяем, был ли ордер уже размещён
        if not order_id:
            # Распечатка полученных данных
            logging.info(Fore.CYAN + f"Получены данные: {message['topic']}" + Style.RESET_ALL)

            # Пример обработки данных ордербука для тикера
            if message['topic'] == f'orderbook.50.{ticker}':
                mid_price, stop_loss, quantity = get_trade_details(message, direction, capital)
                logging.info(Fore.BLUE + f"{ticker}: Средняя цена: {mid_price}, Стоп-лосс: {stop_loss}, Количество: {quantity}" + Style.RESET_ALL) 
        
                if quantity > 0:
                    # Размещение ордера
                    order_id = place_order(ticker, mid_price, quantity, direction, stop_loss)
                    if order_id:
                        logging.info(Fore.GREEN + f"Ордер успешно размещён с ID: {order_id}" + Style.RESET_ALL)
                        # order_placed = True  # Флаг, что ордер размещён
                        return order_id
                    else:
                        logging.error(f"Не удалось разместить ордер по {ticker}.")
                else:
                    logging.error(f"Не удалось получить данные ордербука по {ticker}.")
    
    ws = WebSocket(
    testnet=True,
    channel_type="linear",
    )
    
    # Подписка на поток данных WebSocket
    ws.orderbook_stream(
        depth=50,  # Можно выбрать 1, 50, 200 или 500
        symbol=ticker,
        callback=handle_message
    )

    # Ожидание работы WebSocket-соединения
    while not order_id:
        pass  # Цикл для ожидания размещения ордера, можно заменить на более изящное ожидание

    return order_id

# Пример вызова функции
# initialise_order_execution("ENAUSDT", "Long", 2000)