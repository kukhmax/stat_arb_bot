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
        close = float(price_values[4])
        if math.isnan(close):
            return []
        close_prices.append(close)
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


# orderbook = {'topic': 'orderbook.50.AXSUSDT', 'type': 'snapshot', 'ts': 1727357190123, 'data': {'s': 'AXSUSDT', 'b': [['4.715', '76.3'], ['4.714', '84.9'], ['4.713', '77.3'], ['4.712', '99.7'], ['4.711', '92.6'], ['4.710', '90.6'], ['4.709', '87.1'], ['3.397', '1.1'], ['2.713', '4800.0'], ['0.625', '500.0']], 'a': [['4.891', '266.0'], ['4.892', '645.6'], ['4.893', '663.9'], ['4.905', '72.7'], ['4.906', '81.4'], ['4.907', '71.2'], ['4.908', '72.7'], ['4.909', '81.4'], ['4.910', '66.6'], ['4.911', '101.4'], ['4.912', '80.2'], ['5.042', '81.7'], ['5.090', '570.1'], ['5.091', '785.7'], ['5.092', '617.5'], ['5.093', '762.4'], ['5.094', '753.3'], ['5.095', '613.0'], ['5.096', '820.1'], ['5.097', '821.0'], ['5.172', '81.7'], ['5.302', '81.7'], ['5.431', '81.7'], ['5.561', '81.7'], ['5.691', '81.7'], ['5.821', '81.7'], ['5.950', '81.7'], ['6.080', '80.6'], ['6.210', '81.7'], ['6.340', '81.7'], ['6.469', '81.7'], ['6.599', '80.7'], ['6.729', '81.7'], ['6.859', '81.7'], ['19.855', '497.3'], ['70.000', '50.0'], ['85.000', '2.3'], ['108.840', '0.2'], ['110.000', '0.2'], ['146.980', '10.0']], 'u': 702401, 'seq': 20397651896}, 'cts': 1727357149164}

# print(get_trade_details(orderbook, direction="Long", capital=0))