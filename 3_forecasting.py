import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
import warnings
warnings.filterwarnings('ignore')

# Загрузка данных
monthly = pd.read_excel('monthly_total.xlsx')
df_prophet = monthly[['Дата', 'Объем_кг']].rename(columns={'Дата': 'ds', 'Объем_кг': 'y'})

print("=== Улучшенная модель Prophet ===\n")

model = Prophet(
    yearly_seasonality=True,
    seasonality_mode='multiplicative',
    changepoint_prior_scale=0.4,      # делаем тренд более гибким
    seasonality_prior_scale=10,
    interval_width=0.90
)

model.fit(df_prophet)

# Прогноз на 8 месяцев вперёд
future = model.make_future_dataframe(periods=8, freq='M')
forecast = model.predict(future)

# Результат
print("ПРОГНОЗ НА СЛЕДУЮЩИЕ МЕСЯЦЫ:")
forecast_next = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(8).copy()
forecast_next['ds'] = forecast_next['ds'].dt.strftime('%Y-%m')
print(forecast_next.round(0))

forecast_next.to_excel('forecast_improved.xlsx', index=False)

# Качество
historical = forecast[['ds', 'yhat']].merge(df_prophet, on='ds')
mae = mean_absolute_error(historical['y'], historical['yhat'])
mape = mean_absolute_percentage_error(historical['y'], historical['yhat']) * 100
print(f"\nКачество улучшенной модели:  MAE = {mae:.0f} кг | MAPE = {mape:.1f}%")

# Графики
model.plot(forecast)
plt.title('Улучшенный прогноз продаж (Prophet)')
plt.savefig('forecast_improved.png', dpi=200, bbox_inches='tight')
print("\nГрафики и файл сохранены.")