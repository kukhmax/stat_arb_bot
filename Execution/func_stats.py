import statsmodels.api as sm
import pandas as pd
from statsmodels.tsa.stattools import coint
from config_execution_api import Z_SCORE_WINDOW


# Calculate Z-Score
def calculate_zscore(spread):
    df = pd.DataFrame(spread)
    mean = df.rolling(window=Z_SCORE_WINDOW).mean()
    std = df.rolling(window=Z_SCORE_WINDOW).std()
    zscore = (df - mean) / std
    return zscore.squeeze().astype(float).values  # squeeze для упрощения DataFrame в Series

# Calculate spread
def calculate_spread(series_1, series_2, hedge_ratio):
    spread = pd.Series(series_1) - (pd.Series(series_2) * hedge_ratio) 
    return spread

# Calculate metrics
def calculate_metrics(series_1, series_2):
    coint_res = coint(series_1, series_2)
    coint_flag = 0
    coint_t, p_value, crit_values = coint_res
    critical_value = crit_values[1]
    model = sm.OLS(series_1, sm.add_constant(series_2)).fit()
    hedge_ratio = model.params[0]  # Получаем коэффициент хеджирования (hedge ratio)
    
    spread = calculate_spread(series_1, series_2, hedge_ratio)
    zscore_list = calculate_zscore(spread)
    

    if p_value < 0.5 and coint_t < critical_value:  # Используем 5%-ый критический уровень
        coint_flag = 1

    return coint_flag, zscore_list.tolist()