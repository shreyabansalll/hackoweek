import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing


df = pd.read_csv(r"C:\\Users\\aarya\\OneDrive\Desktop\\hack o week\\hack o week\\library_energy_exam_dataset.csv")
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)

energy_series = df['energy_kwh']


model = ExponentialSmoothing(
    energy_series,
    trend='add',
    seasonal=None
)

model_fit = model.fit()


forecast_days = 30
forecast = model_fit.forecast(forecast_days)

semester_forecast = forecast.sum()

print("Predicted Semester-End Energy Usage (kWh):",
      round(semester_forecast, 2))
