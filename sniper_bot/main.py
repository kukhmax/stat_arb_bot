import ccxt
import time
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Уровень логирования
    format='%(asctime)s - %(levelname)s - %(message)s',  # Формат сообщения
    handlers=[
        logging.FileHandler('sniper_bot.log'),  # Запись в файл
        logging.StreamHandler()  # Вывод в консоль
    ]
)

# Конфигурационные параметры
API_KEY = 'mx0vglig6IP8XRosgE'
API_SECRET = '64580d47c4b24e55816771bf18ee2f37'
SYMBOL = 'PROTON/USDT'

# Создание объекта биржи
exchange = ccxt.mexc({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True,  # Включение лимита на запросы
})

# Функция для получения текущей цены актива
def get_current_price(symbol):
    try:
        ticker = exchange.fetch_ticker(symbol)
        # logging.info(f"Текущая цена {symbol}: {ticker}")
        return ticker['last']
           
    except Exception as e:
        logging.error(f"Ошибка при получении цены для {symbol}: {e}")
        return None

# Функция для отправки рыночного ордера на покупку
def create_market_order(symbol, quantity):
    try:
        order = exchange.create_order(symbol,side='buy', type='market', amount=quantity)
        return order
    except Exception as e:
        logging.error(f"Ошибка при создании ордера {symbol}: {e}")
        return None

# Основная функция снайпер бота
def sniper_bot(symbol):
    logging.info(f"Смотрим за началом торгов для {symbol}...")
    
    while True:
        try:
            # Получение текущей цены
            price = get_current_price(symbol)
            
            if price is None:
                logging.warning("Не удалось получить цену, пробуем снова...")
                time.sleep(1)
                continue
            
            logging.info(f"Текущая цена {symbol}: {price}")

            # Проверка, запускались ли торги (пример, если цена выше нуля)
            if price > 0:  # Здесь вы можете добавить логику определения старта торгов
                logging.info("Торговля запущена! Выполняем рыночный ордер...")
                quantity = round(8 / price, 2)
                logging.info(f"Количество {symbol} для ордера: {quantity}")
                response = create_market_order(symbol, quantity)  # Установите нужное количество
                
                if response:
                    logging.info(f"Ответ от MEXC: {response}")
                # break  # Выход из цикла после выполнения ордера

        except Exception as e:
            logging.error(f"Общая ошибка: {e}")
        
        time.sleep(0.8)  # Ждать 1 секунду перед следующим запросом

# Запуск снайпер бота
if __name__ == '__main__':
    print(exchange.fetch_order_book(SYMBOL))
    sniper_bot(SYMBOL)