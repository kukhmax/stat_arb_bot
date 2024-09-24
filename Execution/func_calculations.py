import math
from config_execution_api import (
    TICKER_1,
    ROUNDING_TICKER_1,
    ROUNDING_TICKER_2,
    QUANTITY_ROUNDING_TICKER_1,
    QUANTITY_ROUNDING_TICKER_2,
    STOP_LOSS_FAIL_SAFE, 
)


# Puts all close prices in a list
def extract_close_prices(prices):
    close_prices = []
    for price_values in prices:
        if math.isnan(price_values["close"]):
            return []
        close_prices.append(price_values["close"])
    return close_prices

# Get trade details and latest prices
def get_trade_details(orderbook, direction="Long", capital=0):
    # Set calculation and output variables
    price_rounding = 20
    quantity_rounding = 20
    mid_price = 0
    quantity = 0
    stop_loss = 0

    # Get prices, stop loss and quantity
    if orderbook:
        price_rounding = ROUNDING_TICKER_1 if orderbook["data"]["s"] == TICKER_1 else ROUNDING_TICKER_2
        quantity_rounding = QUANTITY_ROUNDING_TICKER_1 if orderbook["data"]["s"] == TICKER_1 else QUANTITY_ROUNDING_TICKER_2
        
        bid_items_list = [float(bid[0]) for bid in orderbook["data"]["b"]]
        ask_items_list = [float(ask[0]) for ask in orderbook["data"]["a"]]

        # Calculate price, size, stop loss and average liquidity
        if len(ask_items_list) > 0 and len(bid_items_list) > 0:
            
            # Get nearest ask, nearest bid and orderbook spread
            nearest_ask = ask_items_list[0]
            nearest_bid = bid_items_list[0]

            # Calculate hard stop loss
            if direction == "Long":
                mid_price = nearest_bid   # placing at Bid has high probability of not being cancelled, but may not fill
                stop_loss = round(mid_price * (1 - STOP_LOSS_FAIL_SAFE), price_rounding)
            else:
                mid_price = nearest_ask  # placing at Ask has high probability of not being cancelled, but may not fill
                stop_loss = round(mid_price * (1 + STOP_LOSS_FAIL_SAFE), price_rounding)
                
            # Рассчитываем количество
            quantity = round(capital / mid_price, quantity_rounding)

    return mid_price, stop_loss, quantity





# from pybit.unified_trading import WebSocket
# # WebSocket-соединение
# ws = WebSocket(
#     testnet=True,
#     channel_type="linear",  # Для фьючерсов, для спота используйте "spot"
# )

# # Callback-функция для обработки потока ордербука
# def handle_message(message):
#     # Распечатка полученных данных (можно заменить на логику обработки)
#     print(f"Получены данные: {message}")
    
#     # Пример обработки данных ордербука для пары TICKER_1
#     if message['topic'] == f'orderbook.50.{TICKER_1}':
#         mid_price, stop_loss, quantity = get_trade_details(message, direction="Long", capital=1000)
#         print(f"TICKER_1: Средняя цена: {mid_price}, Стоп-лосс: {stop_loss}, Количество: {quantity}")
    
#     # # Пример обработки данных ордербука для пары TICKER_2
#     # elif message['topic'] == f'orderbook.50.{TICKER_2}':
#     #     mid_price, stop_loss, quantity = get_trade_details(message["data"], direction="Short", capital=1000)
#     #     print(f"TICKER_2: Средняя цена: {mid_price}, Стоп-лосс: {stop_loss}, Количество: {quantity}")

# # Подписка на поток данных для двух торговых пар
# ws.orderbook_stream(
#     depth=50,  # Можно выбрать 1, 50, 200 или 500
#     symbol=TICKER_1,
#     callback=handle_message
# )

# from time import sleep
# # Постоянная работа WebSocket-соединения
# while True:
#     sleep(1)