from func_price_kline import get_price_kline
import json

# Store price history for all available prices
def store_price_history(symbols):
    
    # Get prices and store in DataFrame
    counts = 0
    price_history_dict = {}
    for sym in symbols:
        try:
            symbol_name = sym['symbol']
            price_history = get_price_kline(symbol_name)
            
            if price_history:
                price_history_dict[symbol_name] = price_history['result']['list']
                counts += 1
                print(f"{counts} items stored")
            else:
                print(f"{counts} items not stored")
        except Exception as e:
            print(f"Error: {e}")
        
    # Store price history in json
    if len(price_history_dict) > 0:
        with open('1_price_list.json', 'w') as f:
            json.dump(price_history_dict, f, indent=4)
        print(f"Prices save successfully. Total {counts} items")
    
    return 