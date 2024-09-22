"""STRATAGY CODE"""

import json
import pandas as pd
from func_get_symbols import get_tradeable_symbols
from func_prices_json import store_price_history
from func_cointegration import get_cointegrated_pairs

if __name__ == "__main__":
    
    # # STEP 1 - Get list of symbols
    # print("Getting symbols...")
    # sym_responce = get_tradeable_symbols()
    
    # # STEP 2 - Constaract and save price history
    # print("Constructing and saving price data to JSON...")
    # print(len(sym_responce))
    # if len(sym_responce) > 0:
    #     store_price_history(sym_responce)
    
    # STEP 3 - Find Cointegrated pairs
    print("Calculating co-integrated...")
    with open('1_price_list.json') as f:
        price_history = json.load(f)

    if len(price_history) > 0:
        coin_pairs = get_cointegrated_pairs(price_history)
    print("Done!")
    