import pandas as pd
import matplotlib.pyplot as plt
from func_cointegration import (
    extract_close_prices,
    calculate_cointegration,
    calculate_spread,
    calculate_zscore
)

# Функция для построения графиков цен и трендов
def plot_trends(sym_1, sym_2, price_data, save_path=None):

    # Извлекаем цены для обоих активов
    prices_1 = extract_close_prices(price_data[sym_1])
    prices_2 = extract_close_prices(price_data[sym_2])

    # Рассчитываем спред, коэффициент хеджирования и Z-Score
    coint_flag, p_value, t_value, c_value, hedge_ratio, zero_crossing = calculate_cointegration(prices_1, prices_2)
    spread = calculate_spread(prices_1, prices_2, hedge_ratio)
    zscore = calculate_zscore(spread)

    # Создаём DataFrame с процентными изменениями для обоих активов
    df = pd.DataFrame({sym_1: prices_1, sym_2: prices_2})
    df[f"{sym_1}_pct"] = df[sym_1] / df[sym_1].iloc[0]
    df[f"{sym_2}_pct"] = df[sym_2] / df[sym_2].iloc[0]

    # Преобразуем данные в формат numpy для графиков
    series_1 = df[f"{sym_1}_pct"].to_numpy()
    series_2 = df[f"{sym_2}_pct"].to_numpy()

    # Сохраняем результаты для бэктестинга
    df_backtest = pd.DataFrame({
        sym_1: prices_1,
        sym_2: prices_2,
        "Spread": spread,
        "ZScore": zscore
    })
    df_backtest.to_csv("3_backtest_file.csv", index=True)
    print("Файл для бэктестинга сохранён.")

    # Построение графиков
    fig, axs = plt.subplots(3, figsize=(16, 8))
    fig.suptitle(f"Price and Spread - {sym_1} vs {sym_2}")

    # График процентных изменений цен активов
    axs[0].plot(series_1, label=sym_1)
    axs[0].plot(series_2, label=sym_2)
    # axs[0].set_title(f'Процентное изменение цен {sym_1} и {sym_2}')
    axs[0].legend()

     # График спреда
    axs[1].plot(spread, label='Spread')
    axs[1].axhline(0, color='gray', linestyle='--', linewidth=1, alpha=0.7)  # Добавляем пунктирную линию на 0
    # axs[1].set_title(f'Спред между {sym_1} и {sym_2}')
    axs[1].legend()

    # График Z-Score
    axs[2].plot(zscore, label='Z-Score')
    axs[2].axhline(0, color='gray', linestyle='--', linewidth=1, alpha=0.7)  # Добавляем пунктирную линию на 0
    # axs[2].set_title(f'Z-Score для {sym_1} и {sym_2}')
    axs[2].legend()
    
    save_path = f'{sym_1} vs {sym_2} - backtest.png'
    
    # Сохранение графиков в файл, если путь задан
    if save_path:
        plt.savefig(save_path, bbox_inches='tight')  # Сохраняем график
        print(f"График сохранён в файл: {save_path}")
    
    # # Показ графиков
    # plt.tight_layout()
    # plt.show()
    
    # Закрываем фигуру, чтобы освободить память
    plt.close(fig)