import json
from config_strategy_api import session

# Get symbols that are tradeable
def get_tradeable_symbols():
    
    sym_list = []
    symbols = session.get_instruments_info(
        category='spot',
        status="Trading"
    )
    if 'retCode' in symbols.keys() and symbols['retMsg'] == "OK":
        symbols = symbols['result']['list']
        for symbol in symbols:
            if symbol["quoteCoin"] == "USDT":
                sym_list.append(symbol)
        # with open('symbols.json', 'w') as f:
        #     json.dump(sym_list, f)
    return sym_list

