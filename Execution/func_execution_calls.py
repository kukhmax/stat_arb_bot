import logging
from config_execution_api import session, ws,LIMIT_ORDER_BASIS
from func_calculations import get_trade_details


# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


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
        if response["retCode"] == 0:
            logging.info(f"Плечо успешно установлено для {ticker}")
        else:
            logging.error(f"Ошибка установки плеча для {ticker}: {response['retMsg']}")
    except Exception as e:
        logging.error(f"Исключение при установке плеча для {ticker}: {e}")

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
            logging.info(f"Ордера на {side} {quantity} {ticker} успешно размещён.")
            return order["result"]["orderId"]
        else:
            logging.error(f"Ошибка размещения ордера по {ticker}: {order['retMsg']}")
            return None
    except Exception as e:
        logging.error(f"Исключение при размещении ордера по {ticker}: {e}")
        return None
    
   
def initialise_order_execution(ticker, direction, capital):
    
    # Переменная для отслеживания, был ли размещён ордер
    order_placed = False

    # Callback-функция для обработки потока ордербука
    def handle_message(message):
        nonlocal order_placed  # Доступ к переменной из внешней области видимости

        # Проверяем, был ли ордер уже размещён
        if not order_placed:
            # Распечатка полученных данных
            logging.info(f"Получены данные: {message['topic']}")

            # Пример обработки данных ордербука для тикера
            if message['topic'] == f'orderbook.50.{ticker}':
                mid_price, stop_loss, quantity = get_trade_details(message, direction, capital)
                logging.info(f"{ticker}: Средняя цена: {mid_price}, Стоп-лосс: {stop_loss}, Количество: {quantity}")
        
                if quantity > 0:
                    # Размещение ордера
                    order_id = place_order(ticker, mid_price, quantity, direction, stop_loss)
                    if order_id:
                        logging.info(f"Ордер успешно размещён с ID: {order_id}")
                        order_placed = True  # Флаг, что ордер размещён
                    else:
                        logging.error(f"Не удалось разместить ордер по {ticker}.")
                else:
                    logging.error(f"Не удалось получить данные ордербука по {ticker}.")
    
    # Подписка на поток данных WebSocket
    ws.orderbook_stream(
        depth=50,  # Можно выбрать 1, 50, 200 или 500
        symbol=ticker,
        callback=handle_message
    )

    # Ожидание работы WebSocket-соединения
    while not order_placed:
        pass  # Цикл для ожидания размещения ордера, можно заменить на более изящное ожидание


# Пример вызова функции
# initialise_order_execution("ENAUSDT", "Long", 2000)