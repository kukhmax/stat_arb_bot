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
    
   
# Инициализация исполнения ордера
def initialise_order_execution(ticker, direction, capital):
    
    # Callback-функция для обработки потока ордербука
    def handle_message(message):
        # Распечатка полученных данных (можно заменить на логику обработки)
        logging.info(f"Получены данные: {message['topic']}")
        
        # Пример обработки данных ордербука для пары TICKER_1
        if message['topic'] == f'orderbook.50.{ticker}':
            mid_price, stop_loss, quantity = get_trade_details(message, direction, capital)
            logging.info(f"{ticker}: Средняя цена: {mid_price}, Стоп-лосс: {stop_loss}, Количество: {quantity}")
    
            if quantity > 0:
                # Размещение ордера
                order_id = place_order(ticker, mid_price, quantity, direction, stop_loss)
                if order_id:
                    logging.info(f"Ордера успешно размещён с ID: {order_id}")
                    return order_id
                else:
                    logging.error(f"Не удалось разместить ордер по {ticker}.")
            else:
                logging.error(f"Не удалось получить данные ордербука по {ticker}.")
    
    ws.orderbook_stream(
                depth=50,  # Можно выбрать 1, 50, 200 или 500
                symbol=ticker,
                callback=handle_message
            )
    # return None

# Пример вызова функции
initialise_order_execution("ENAUSDT", "Long", 2000)
