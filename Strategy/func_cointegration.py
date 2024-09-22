from statsmodels.tsa.stattools import coint
import statsmodels.api as sm
import pandas as pd
import numpy as np
from itertools import combinations


# Calculate spread
def calculate_spread(series_1, series_2, hedge_ratio):
    spread = pd.Series(series_1) - (pd.Series(series_2) * hedge_ratio) 
    return spread

# Calculate co-integration
def calculate_cointegration(series_1, series_2):
    coint_res = coint(series_1, series_2)
    coint_flag = 0
    coint_t, p_value, crit_values = coint_res
    model = sm.OLS(series_1, sm.add_constant(series_2)).fit()
    hedge_ratio = model.params[1]  # Получаем коэффициент хеджирования (hedge ratio)
    
    spread = calculate_spread(series_1, series_2, hedge_ratio)
    sign_changes = np.sign(spread)
    # np.diff возвращает разности между соседними элементами; когда знак меняется, разность будет не равна 0
    zero_crossings = np.sum(np.diff(sign_changes) != 0)
    # zero_crossings = len(np.where(np.diff(np.sign(spread)))[0])    #np.sum(np.diff(np.sign(spread)) != 0)  # Количество пересечений 0

    if p_value < 0.5 and coint_t < crit_values[1]:  # Используем 5%-ый критический уровень
        coint_flag = 1

    return (
        coint_flag, 
        round(p_value, 2), 
        round(coint_t, 2), 
        round(crit_values[1], 2), 
        round(hedge_ratio, 2), 
        zero_crossings
    )

# Put close prices into a list
def extract_close_prices(prices):
    close_prices = []
    for item in prices:
        if not item[4]:
            return []
        close_prices.append(float(item[4]))
        # print(close_prices)
    return close_prices

# Calculate Cointagrated Pairs
def get_cointegrated_pairs(prices):
    
    coint_pair_list = []
    included_pairs = set()

    for sym_1, sym_2 in combinations(prices.keys(), 2):  # Перебираем комбинации пар
        series_1 = extract_close_prices(prices[sym_1])
        series_2 = extract_close_prices(prices[sym_2])

        if not series_1 or not series_2:  # Пропускаем, если не можем получить цены
            continue

        unique_key = tuple(sorted([sym_1, sym_2]))  # Уникальная комбинация
        if unique_key in included_pairs:
            break

        coint_flag, p_value, t_value, c_value, hedge_ratio, zero_crossings = calculate_cointegration(series_1, series_2)

        if coint_flag == 1:
            included_pairs.add(unique_key)
            coint_pair_list.append({
                "sym_1": sym_1,
                "sym_2": sym_2,
                "p_value": p_value,
                "t_value": t_value,
                "c_value": c_value,
                "hedge_ratio": hedge_ratio,
                "zero_crossings": zero_crossings
            })

    # Сохранение результатов в файл
    df_coint = pd.DataFrame(coint_pair_list)
    df_coint = df_coint.sort_values("zero_crossings", ascending=False)
    df_coint.to_csv("2_cointegrated_pairs.csv", index=False)
    
    return df_coint