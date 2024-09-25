from config_execution_api import (
    SIGNAL_POSITIVE_TICKER,
    SIGNAL_NEGATIVE_TICKER,
    session
)
import logging

# Настроим базовое логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Get position inforamtion
def get_position_info(ticker):
    try:
        position = session.get_positions(
            category="linear",
            symbol=ticker,
        )
        
        # Declare output variables
        side = ""
        size = 0

    # Проверяем успешность запроса
        if position.get('retMsg') == "OK":
            if position['result']['list']:
                pos_info = position['result']['list'][0]
                side = pos_info['side']
                size = float(pos_info['size'])
                logging.info(f"Получена позиция по {ticker}: {side}, {size}")
            else:
                logging.warning(f"Позиции по {ticker} не найдены.")
        else:
            logging.error(f"Ошибка получения позиции по {ticker}: {position.get('retMsg')}")
        
        return side, size
    except Exception as e:
        logging.error(f"Ошибка при получении позиции по {ticker}: {e}")
        return None, 0.0

#  Place market close order
def place_market_close_order(ticker, side, size):
    try:
        session.place_order(
            category="linear",
            symbol=ticker,
            side=side,
            orderType="Market",
            qty=size,
            timeInForce="GTC",
        )
        logging.info(f"Рыночный ордер для закрытия позиции по {ticker} успешно отправлен: {side}, {size}")
    except Exception as e:
        logging.error(f"Ошибка при отправке рыночного ордера для {ticker}: {e}")

# Close all positions for both tickers
def close_all_positions(kill_switch):
    
    try:
        # Отмена всех активных ордеров
        session.cancel_all_orders(category="linear", symbol=SIGNAL_POSITIVE_TICKER)
        logging.info(f"Все активные ордера по {SIGNAL_POSITIVE_TICKER} отменены.")
        
        session.cancel_all_orders(category="linear", symbol=SIGNAL_NEGATIVE_TICKER)
        logging.info(f"Все активные ордера по {SIGNAL_NEGATIVE_TICKER} отменены.")

        # Получаем информацию по позициям
        side_1, size_1 = get_position_info(SIGNAL_POSITIVE_TICKER)
        side_2, size_2 = get_position_info(SIGNAL_NEGATIVE_TICKER)

        # Закрываем позиции, если они есть
        if size_1 > 0:
            opposite_side = "Sell" if side_1 == "Buy" else "Buy"
            place_market_close_order(SIGNAL_POSITIVE_TICKER, opposite_side, size_1)

        if size_2 > 0:
            opposite_side = "Sell" if side_2 == "Buy" else "Buy"
            place_market_close_order(SIGNAL_NEGATIVE_TICKER, opposite_side, size_2)

        # Устанавливаем kill_switch в 0 после завершения
        kill_switch = 0
        logging.info("Все позиции закрыты, kill_switch установлен в 0.")
    except Exception as e:
        logging.error(f"Ошибка при закрытии позиций: {e}")
    
    return kill_switch

