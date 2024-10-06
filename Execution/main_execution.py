# Remove Pandas Future Warnings
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import json
import time
import logging
from config_execution_api import SIGNAL_POSITIVE_TICKER, SIGNAL_NEGATIVE_TICKER, ws
from func_positon_calls import open_position_confirmation, active_position_confirmation
from func_execution_calls import set_leverage
from func_trade_management import manage_new_trades
from func_close_positions import close_all_positions
from func_get_zscore import get_latest_zscore

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s - [%(funcName)s:%(lineno)d]",  # Формат логов с именем функции и номером строки
    datefmt="%Y-%m-%d %H:%M:%S"
    )

# Save status
def save_status(dict):
    with open("status.json", "w") as fp:
        json.dump(dict, fp, indent=4)

""" RUN STATBOT """

if __name__ == "__main__":
    
    # Initial printout
    logging.info("Запуск статуса бота ...")
    
    # Initialise variables
    status_dict = {"message": "starting..."}
    order_long = {}
    order_short = {}
    signal_sign_positive = False
    signal_side = ""
    kill_switch = 0
    
    # Save status
    save_status(status_dict)

    # Set leverage in case forgotten to do so on the platform
    logging.info("Setting leverage...")
    set_leverage(SIGNAL_POSITIVE_TICKER)
    set_leverage(SIGNAL_NEGATIVE_TICKER)

    # Commence bot (Начало бота)
    logging.info("Seeking trades...")
    while True:
        
        # Pause - protect API
        time.sleep(3)

        # Check if open trades already exist
        is_p_ticker_open = open_position_confirmation(SIGNAL_POSITIVE_TICKER)
        is_n_ticker_open = open_position_confirmation(SIGNAL_NEGATIVE_TICKER)
        is_p_ticker_active = active_position_confirmation(SIGNAL_POSITIVE_TICKER)
        is_n_ticker_active = active_position_confirmation(SIGNAL_NEGATIVE_TICKER)
        checks_all = [is_p_ticker_open, is_n_ticker_open, is_p_ticker_active, is_n_ticker_active]
        is_manage_new_trades = not any(checks_all)
        
        # Save status
        status_dict["message"] = "Initial checks made..."
        status_dict["checks"] = checks_all
        save_status(status_dict)
        
        # Check for signal and place new trades
        if is_manage_new_trades and kill_switch == 0:
            status_dict["message"] = "Managing new trades..."
            save_status(status_dict)
            kill_switch, signal_side = manage_new_trades(kill_switch)
        
        # Managing open kill switch if positions change or should reach 2
        # Check for signal to be false
        if kill_switch == 1:

            # Get and save the latest z-score
            zscore, signal_sign_positive = get_latest_zscore()
            
            logging.info(f"zscore: {zscore} signal_sign_positive: {signal_sign_positive} signal_side: {signal_side}")

            # Close positions
            if signal_side == "positive" and zscore <= 0:
                kill_switch = 2
            if signal_side == "negative" and zscore >= 0:
                kill_switch = 2

            # Put back to zero if trades are closed
            if is_manage_new_trades and kill_switch != 2:
                kill_switch = 0

        
        # Close all active orders and positions
        if kill_switch == 2:
            logging.info("Closing all positions...")
            status_dict["message"] = "Closing existing trades..."
            save_status(status_dict)
            kill_switch = close_all_positions(kill_switch)

            # Sleep for 5 seconds
            time.sleep(5)