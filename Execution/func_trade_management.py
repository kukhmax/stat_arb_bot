import time
import logging
import inspect
from config_execution_api import (
    ws,
    session,
    SIGNAL_NEGATIVE_TICKER,
    SIGNAL_POSITIVE_TICKER,
    SIGNAL_TRIGGER_THRESH,
    TRADEABLE_CAPITAL_USDT,
    LIMIT_ORDER_BASIS,
    TICKER_1,
    TICKER_2
)
from func_price_calls import get_ticker_trade_liquidity
from func_get_zscore import get_latest_zscore
from func_execution_calls import initialise_order_execution
from func_order_review import check_order

from colorama import Fore, Style

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s - [%(funcName)s:%(lineno)d]",
    datefmt="%Y-%m-%d %H:%M:%S"
    )

# Manage new trade assessment and order placing
def manage_new_trades(kill_switch):

    # Set variables
    order_long_id = ""
    order_short_id = ""
    signal_side = ""
    hot = False
    
    # Get and save the latest z-score
    zscore, signal_sign_positive = get_latest_zscore()   #  ПЕРВАЯ ПОДПИСКА WS !!!!!!!!!!!!!!!!!!!!!!!

    # Switch to hot if meets signal threshold
    # Note: You can add in coint-flag check too if you want extra vigilence
    if abs(zscore) > SIGNAL_TRIGGER_THRESH:
        
        # Active hot trigger
        hot = True
        logging.info("-- Trade Status HOT --")
        logging.info("-- Placing and Monitoring Existing Trades --")
    
    # Place and manage trades
    if hot and kill_switch == 0:
        
        # Get trades history for liquidity
        avg_liquidity_ticker_p, last_price_p = get_ticker_trade_liquidity(SIGNAL_POSITIVE_TICKER)
        avg_liquidity_ticker_n, last_price_n = get_ticker_trade_liquidity(SIGNAL_NEGATIVE_TICKER)

       # Determine long ticker vs short ticker
        if signal_sign_positive:
            # Если сигнал положительный, устанавливаем положительный тикер как длинную позицию,
            # а отрицательный — как короткую. Также присваиваем соответствующие значения ликвидности и цены.
            long_ticker = SIGNAL_POSITIVE_TICKER
            short_ticker = SIGNAL_NEGATIVE_TICKER
            avg_liquidity_long = avg_liquidity_ticker_p
            avg_liquidity_short = avg_liquidity_ticker_n
            last_price_long = last_price_p
            last_price_short = last_price_n
        else:
            # Если сигнал отрицательный, наоборот: отрицательный тикер — длинная позиция, а положительный — короткая.
            long_ticker = SIGNAL_NEGATIVE_TICKER
            short_ticker = SIGNAL_POSITIVE_TICKER
            avg_liquidity_long = avg_liquidity_ticker_n
            avg_liquidity_short = avg_liquidity_ticker_p
            last_price_long = last_price_n
            last_price_short = last_price_p
            
      
        # Капитал делится поровну между длинной и короткой позициями.
        capital_long = TRADEABLE_CAPITAL_USDT * 0.5
        capital_short = TRADEABLE_CAPITAL_USDT - capital_long
        # Рассчитываются начальные объемы для заполнения по ликвидности и цене для обеих позиций.
        initial_fill_target_long_usdt = avg_liquidity_long * last_price_long
        initial_fill_target_short_usdt = avg_liquidity_short * last_price_short
        initial_capital_injection_usdt = min(initial_fill_target_long_usdt, initial_fill_target_short_usdt)

        # Ensure initial cpaital does not exceed limits set in configuration
        if LIMIT_ORDER_BASIS:
            # Если используются лимитные ордера, проверяем, чтобы начальный капитал не превышал доступный капитал для длинной позиции.
            if initial_capital_injection_usdt > capital_long:
                initial_capital_usdt = capital_long
            else:
                initial_capital_usdt = initial_capital_injection_usdt
        else:
            initial_capital_usdt = capital_long
            
        # Оставшийся капитал для длинной и короткой позиций устанавливается
        # равным выделенному капиталу для каждой позиции.
        remaining_capital_long = capital_long
        remaining_capital_short = capital_short
        
        # Trade until filled or signal is false
        order_status_long = ""
        order_status_short = ""
        # счётчики для отслеживания количества попыток размещения ордеров.
        counts_long = 0
        counts_short = 0
        while kill_switch == 0:

            # Если длинный ордер ещё не был размещён (counts_long == 0), выполняется функция initialise_order_execution для длинного тикера, и,
            # если ордер был успешно размещён (order_long_id), 
            # счётчик увеличивается до 1. Оставшийся капитал уменьшается на величину начального капитала для длинной позиции.
            if counts_long == 0:
                order_long_id = initialise_order_execution(long_ticker, "Long", initial_capital_usdt)  #  ВТОРАЯ ПОДПИСКА WS !!!!!!!!!!!!!!!!!!!!!!!
                counts_long = 1 if order_long_id else 0
                remaining_capital_long = remaining_capital_long - initial_capital_usdt

            # Place order - short
            if counts_short == 0:
                order_short_id = initialise_order_execution(short_ticker, "Short", initial_capital_usdt)  #  ТРЕТЬЯ ПОДПИСКА WS !!!!!!!!!!!!!!!!!!!!!!!
                counts_short = 1 if order_short_id else 0
                remaining_capital_short = remaining_capital_short - initial_capital_usdt

            
            # В зависимости от знака z-score определяется, 
            # в какую сторону торгуем: "positive" — если z-score положительный, и "negative" — если отрицательный.
            if zscore > 0:
                signal_side = "postive"
            else:
                signal_side = "negative"
                
            # Если лимитные ордера не используются и оба ордера (длинный и короткий) были размещены,
            # переключатель kill_switch устанавливается в 1 для завершения торговли.
            if not LIMIT_ORDER_BASIS and counts_long and counts_short:
                kill_switch = 1

            # Allow for time to register the limit orders
            time.sleep(3)

            # Получение обновлённого z-score и сигнала.
            zscore_new, signal_sign_p_new = get_latest_zscore()
            print()
            
            logging.info(Fore.MAGENTA + f"count_long = {counts_long} | count_short = {counts_short} | kill_switch = {kill_switch}" + Style.RESET_ALL)
            # Если kill_switch всё ещё равен 0, и обновлённый z-score по-прежнему превышает порог в 90% и знак сигнала не изменился, продолжаем торговлю.
            if kill_switch == 0:
                if abs(zscore_new) > SIGNAL_TRIGGER_THRESH * 0.9 and signal_sign_p_new == signal_sign_positive:
                    logging.info(Fore.CYAN + f"New Z-Score: {zscore_new}" + Style.RESET_ALL)
                    
                    # Check long order status
                    if counts_long == 1:
                        order_status_long = check_order(long_ticker, order_long_id, remaining_capital_long, "Long")

                    # Check short order status
                    if counts_short == 1:
                        order_status_short = check_order(short_ticker, order_short_id, remaining_capital_short, "Short")

                logging.info(Fore.GREEN + f"Order Status Long: " + Fore.YELLOW + f"{order_status_long}" + Style.RESET_ALL + "  ||  " + Fore.RED + f"Order Status Short: " + Fore.YELLOW + f"{order_status_short}" + Style.RESET_ALL)
                
                # If orders still active, do nothing
                if order_status_long == "Order Active" or order_status_short == "Order Active":
                    continue

                # If orders partial fill, do nothing
                if order_status_long == "Partial Fill" or order_status_short == "Partial Fill":
                    continue

                # If orders trade complete, do nothing - stop opening trades
                if order_status_long == "Trade Complete" and order_status_short == "Trade Complete":
                    kill_switch = 1

                # If position filled - place another trade
                if order_status_long == "Position Filled" and order_status_short == "Position Filled":
                    kill_switch = 1

                # If order cancelled for long - try again
                if order_status_long == "Try Again":
                    counts_long = 0

                # If order cancelled for short - try again
                if order_status_short == "Try Again":
                    counts_short = 0

            else:
                # Cancel all active orders
                session.cancel_all_active_orders(symbol=SIGNAL_POSITIVE_TICKER)
                session.cancel_all_active_orders(symbol=SIGNAL_NEGATIVE_TICKER)
                kill_switch = 1

    # Output status
    return kill_switch, signal_side


# manage_new_trades(0)