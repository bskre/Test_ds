import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

from prophet import Prophet
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error

# Загрузка данных
monthly = pd.read_excel('monthly_total.xlsx')
monthly = monthly.sort_values('Дата').reset_index(drop=True)

data = monthly[['Дата', 'Объем_кг']].copy()
y = data['Объем_кг']

print("=== ФИНАЛЬНОЕ СРАВНЕНИЕ МОДЕЛЕЙ ПРОГНОЗИРОВАНИЯ ===\n")

# =============================================
# 1. Prophet (улучшенный)
# =============================================
df_prophet = monthly[['Дата', 'Объем_кг']].rename(columns={'Дата':'ds', 'Объем_кг':'y'})

model_p = Prophet(
    yearly_seasonality=True,
    seasonality_mode='multiplicative',
    changepoint_prior_scale=0.35,
    interval_width=0.90
)
model_p.fit(df_prophet)
future = model_p.make_future_dataframe(periods=6, freq='M')
forecast_p = model_p.predict(future)

# =============================================
# 2. Holt-Winters (Exponential Smoothing)
# =============================================
model_hw = ExponentialSmoothing(
    y, 
    trend='add', 
    seasonal='add', 
    seasonal_periods=12,
    damped_trend=True
).fit(optimized=True)

forecast_hw = model_hw.forecast(6)

# =============================================
# Метрики качества
# =============================================
print("ОЦЕНКА КАЧЕСТВА МОДЕЛЕЙ (на исторических данных):")

# Prophet
pred_p = forecast_p['yhat'].iloc[:len(y)]
mae_p = mean_absolute_error(y, pred_p)
mape_p = mean_absolute_percentage_error(y, pred_p) * 100

# Holt-Winters
mae_hw = mean_absolute_error(y, model_hw.fittedvalues)
mape_hw = mean_absolute_percentage_error(y, model_hw.fittedvalues) * 100

print(f"Prophet          → MAE: {mae_p:.0f} кг | MAPE: {mape_p:.1f}%")
print(f"Holt-Winters     → MAE: {mae_hw:.0f} кг | MAPE: {mape_hw:.1f}%")

# =============================================
# Прогноз на 6 месяцев
# =============================================
future_dates = pd.date_range(start=monthly['Дата'].iloc[-1] + pd.offsets.MonthBegin(1), 
                           periods=6, freq='M')

comparison = pd.DataFrame({
    'Месяц': future_dates.strftime('%Y-%m'),
    'Prophet': forecast_p['yhat'].tail(6).round(0).values,
    'Holt-Winters': forecast_hw.round(0).values,
    'Среднее_двух_моделей': ((forecast_p['yhat'].tail(6).values + forecast_hw.values) / 2).round(0)
})

print("\n" + "="*60)
print("ПРОГНОЗ ПРОДАЖ НА СЛЕДУЮЩИЕ 6 МЕСЯЦЕВ (кг)")
print(comparison)

# Сохранение
comparison.to_excel('final_forecast_comparison.xlsx', index=False)

# =============================================
# График сравнения
# =============================================
plt.figure(figsize=(14, 8))
plt.plot(monthly['Дата'], y, label='Фактические продажи', marker='o', linewidth=2)

plt.plot(future_dates, comparison['Prophet'], label='Prophet', linestyle='--', marker='s')
plt.plot(future_dates, comparison['Holt-Winters'], label='Holt-Winters', linestyle='-.', marker='^')

plt.title('Сравнение прогнозов двух моделей')
plt.xlabel('Дата')
plt.ylabel('Объём продаж, кг')
plt.legend()
plt.grid(True)
plt.savefig('final_models_comparison.png', dpi=200, bbox_inches='tight')

print("\n✅ Всё сохранено:")
print("• final_forecast_comparison.xlsx")
print("• final_models_comparison.png")