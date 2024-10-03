import ccxt
import websockets
import asyncio
import json
import logging
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
logger = logging.getLogger()

API_KEY = 'mx0vglig6IP8XRosgE'
API_SECRET = '64580d47c4b24e55816771bf18ee2f37'

# Initialize MEXC exchange with API keys
exchange = ccxt.mexc({
    'apiKey': API_KEY,
    'secret': API_SECRET,
})

# Track price via websocket
async def track_price(symbol):
    check_status = True
    uri = "wss://wbs.mexc.com/ws"  # Replace with actual MEXC WebSocket URI
    async with websockets.connect(uri) as websocket:
        # Subscribe to ticker data instead of orderbook (if available) for simplicity
        subscribe_message = json.dumps({
            "method":"SUBSCRIPTION",
            "params":[f"spot@public.deals.v3.api@{symbol}"],
        })
        await websocket.send(subscribe_message)
        logger.info(f"Subscribed to {symbol} ticker")

        while check_status:
            try:
                response = await websocket.recv()
                data = json.loads(response)
                logging.info(f"response data is :\n{data}")
                # Extract the price safely (adapt according to actual MEXC response)
                if data['d']:                    
                    price = float(data['d']['deals'][0]['p'])
                    logging.info(f"last price is {price}")
                    if price > 0:
                        quantity = 5 / price
                        logger.info(f"Trading started for {symbol} at price: {price}(amount: {quantity})")
                        
                        order = open_market_order(symbol, quantity)
                        check_status = False
                else:
                    logger.warning(f"Unexpected data format: {data}")
            except Exception as e:
                logger.error(f"Error receiving price data: {e}")
                continue
        
        

# Open a market order when trading starts
def open_market_order(symbol, quantity):
    try:
        exchange.create_order(symbol,side='buy', type='market', amount=quantity)
        # time.sleep(5)
        exchange.create_order(symbol,side='sell', type='market', amount=quantity)
        
        logger.info(f"Market order placed for {symbol}")
        
    except ccxt.BaseError as e:
        logger.error(f"Failed to place market order: {e}")

# Monitor position for loss/profit tracking
async def monitor_position(symbol, order_id):
    while True:
        try:
            orders = exchange.fetch_orders(symbol)
            my_position = [o for o in orders if o['id'] == order_id][0]
            current_price = exchange.fetch_order_book(symbol)
            
            current_usdt = my_position['amount'] * current_price['bids'][0][0]
            start_usdt = my_position['amount'] * my_position['average']
            pnl = current_usdt - start_usdt
            pnl_percentage = pnl / (start_usdt * 0.01)
            logging.info(f"Current pnl: {pnl} ({pnl_percentage}%)")
            await asyncio.sleep(2)  # Re-check every second
            exchange.create_order(symbol,side='sell', type='market', amount=my_position['amount'])

        except ccxt.BaseError as e:
            logger.error(f"Error monitoring position: {e}")
        except Exception as e:
            logger.error(f"Unexpected error monitoring position: {e}")

# Main entry point
async def main(symbol):
    try:
        logger.info("Starting sniper bot...")
        order_id = await track_price(symbol)
        # Check for profit or loss
        # logger.info("Monitoring position...")
        # await monitor_position(symbol, order_id)

    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    symbol = "FTONUSDT"  
    asyncio.run(main(symbol))
