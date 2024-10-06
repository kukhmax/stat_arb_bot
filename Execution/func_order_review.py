import logging
from time import sleep
from func_positon_calls import (
    query_existing_order,
    get_open_positions,
    get_active_positions
)
from func_calculations import get_trade_details
from pybit.unified_trading import WebSocket

from colorama import Fore, Style


logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s - [%(funcName)s:%(lineno)d]",  # Формат логов с именем функции и номером строки
    datefmt="%Y-%m-%d %H:%M:%S"
    )

def check_order(ticker, order_id, remaining_capital, direction="Long"):
    
    # Переменные для хранения последней цены
    mid_price = None

    # Callback-функция для обработки данных ордербука
    def handle_message(message):
        nonlocal mid_price
        if message['topic'] == f'orderbook.50.{ticker}':
            mid_price, _, _ = get_trade_details(message)
            # logging.info(Fore.WHITE + f"Средняя цена для {ticker}: {mid_price}" + Style.RESET_ALL)

    # Подписка на WebSocket поток для получения данных о стакане
    
    ws = WebSocket(
        testnet=True,
        channel_type="linear",
    )
    
    ws.orderbook_stream(
        depth=50,  # Глубина стакана
        symbol=ticker,
        callback=handle_message
    )
    
    # Ожидание получения данных через WebSocket
    while mid_price is None:
        if mid_price:
            ws.exit()  # Останавливаем WebSocket
            logging.info(Fore.MAGENTA + "WebSocket соединение закрыто." + Style.RESET_ALL)
        sleep(0.3)
    
    # Получение деталей ордера
    order_price, order_quantity, order_status = query_existing_order(ticker, order_id)

    # Получение информации о текущих открытых позициях
    position_price, position_quantity = get_open_positions(ticker, direction)

    # Проверка статуса ордера и позиций для принятия решений

    # 1. Если количество позиции больше или равно оставшемуся капиталу
    if position_quantity >= remaining_capital and position_quantity > 0:
        logging.info(Fore.GREEN + f"Позиция заполнена: {position_quantity}, оставшийся капитал: {remaining_capital}" + Style.RESET_ALL)
        return F"Trade Complete"

    # 2. Если ордер был полностью заполнен
    if order_status == "Filled":
        logging.info(Fore.GREEN + f"Ордер {order_id} полностью выполнен." + Style.RESET_ALL)
        return "Position Filled"

    # 3. Если ордер активен (новый или создан)
    if order_status == "New":
        logging.info(Fore.GREEN + f"Ордер {order_id} активен." + Style.RESET_ALL)
        return "Order Active"

    # 4. Если ордер частично заполнен
    if order_status == "PartiallyFilled":
        logging.info(Fore.GREEN + f"Ордер {order_id} частично заполнен." + Style.RESET_ALL)
        return "Partial Fill"

    # 5. Если ордер отменён или отклонён
    cancel_items = ["Cancelled", "Rejected", "Triggered", "Deactivated"]
    if order_status in cancel_items:
        logging.info(Fore.GREEN + f"Ордер {order_id} был отменён или отклонён." + Style.RESET_ALL)
        return "Try Again"

    # Если ничего не подошло
    return Fore.RED + "Unknown Status" + Style.RESET_ALL




# Пример вызова функции
# check_order("AXSUSDT", "order12345", 1000, "Long")


# orderStatus

# open status

# New              order has been placed successfully
# PartiallyFilled
# Untriggered        Conditional orders are created

# closed status

# Rejected
# PartiallyFilledCanceled        Only spot has this order status
# Filled
# Cancelled            In derivatives, orders with this status may have an executed qty
# Triggered            instantaneous state for conditional orders from Untriggered to New
# Deactivated           UTA: Spot tp/sl order, conditional order, OCO order are cancelled before they are triggered