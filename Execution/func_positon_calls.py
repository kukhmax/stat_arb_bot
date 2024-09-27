import logging
from config_execution_api import session


logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s - [%(funcName)s:%(lineno)d]",  # Формат логов с именем функции и номером строки
    datefmt="%Y-%m-%d %H:%M:%S"
    )

# Проверка на наличие открытой позиции
def open_position_confirmation(ticker):
    try:
        position = session.get_positions(
            category="linear",
            symbol=ticker,
        )
        if position.get('retMsg') == "OK":
            for item in position['result']['list']:
                size = float(item['size'])
                if size > 0:
                    logging.info(f"Position {item['symbol']} opened with size: {item['size']}")
                    return True
        logging.info(f"Нет открытых позиций по тикеру {ticker}.")
    except Exception as e:
        logging.error(f"Ошибка при проверке позиции для {ticker}: {e}")
        return True
    return False

# Проверка на активные ордера
def active_position_confirmation(ticker):
    try:
        active_orders = session.get_open_orders(
            category="linear",
            symbol=ticker,
            openOnly=0,
            limit=5,
        )
        if active_orders.get('retMsg') == "OK" and active_orders['result']['list']:
            logging.info(f"There are {len(active_orders['result']['list'])} active orders for {ticker}.  ")
            return True
        logging.info(f"Нет активных ордеров для {ticker}.")
    except Exception as e:
        logging.error(f"Ошибка при проверке активных ордеров для {ticker}: {e}")
        return True
    return False

# Получение цены и объёма открытой позиции
def get_open_positions(ticker, direction="Long"):
    try:
        position = session.get_positions(
            category="linear",
            symbol=ticker,
        )
        print(position)
        if position["ret_msg"] == "OK":
            for pos in position["result"]["list"]:
                if float(pos["size"]) > 0:
                    order_price = float(pos["entryPrice"])
                    order_quantity = float(pos["size"])
                    logging.info(f"Цена позиции {ticker}: {order_price}, Объём: {order_quantity}")
                    return order_price, order_quantity
        logging.info(f"Нет открытых позиций по тикеру {ticker}.")
    except Exception as e:
        logging.error(f"Ошибка при получении позиции для {ticker}: {e}")
        return 0, 0
    return 0, 0
        
# Получение цены и объёма активной позиции
def get_active_positions(ticker):
    try:
        active_order = session.get_open_orders(
            category="linear",
            symbol=ticker,
            openOnly=0,
            limit=5,
        )
        print(active_order)
        
        if active_order["retCode"] == 0:
            if active_order["result"]["list"]:
                order_price = float(active_order["result"]["list"][0]["price"])
                order_quantity = float(active_order["result"]["list"][0]["qty"])
                logging.info(f"Активный ордер по {ticker}: Цена: {order_price}, Объём: {order_quantity}")
                return order_price, order_quantity

        logging.info(f"Нет активных ордеров по тикеру {ticker}.")
    except Exception as e:
        logging.error(f"Ошибка при получении активных ордеров для {ticker}: {e}")
        return 0, 0
    return 0, 0

# Запрос существующего ордера
def query_existing_order(ticker, order_id):
    try:
        order = session.get_open_orders(
            category="linear",
            symbol=ticker,
            orderId=order_id
        )
        if order["retCode"] == 0:
            order_price = float(order["result"]["list"][0]["price"])
            order_quantity = float(order["result"]["list"][0]["qty"])
            order_status = order["result"]["list"][0]["orderStatus"]
            logging.info(f"Ордер {order_id} по {ticker}: Цена: {order_price}, Объём: {order_quantity}, Статус: {order_status}")
            return order_price, order_quantity, order_status

        logging.info(f"Ордер {order_id} не найден для {ticker}.")
    except Exception as e:
        logging.error(f"Ошибка при запросе ордера {order_id} для {ticker}: {e}")
        return 0, 0, 0
    return 0, 0, 0
