import os
import pandas as pd
from databricks import sql
from dotenv import load_dotenv
from prophet import Prophet
import matplotlib.pyplot as plt

load_dotenv()
SERVER_HOSTNAME = os.getenv("DATABRICKS_SERVER_HOSTNAME")
HTTP_PATH = os.getenv("DATABRICKS_HTTP_PATH")
ACCESS_TOKEN = os.getenv("DATABRICKS_TOKEN")

if not all([SERVER_HOSTNAME, HTTP_PATH, ACCESS_TOKEN]):
    raise ValueError("Databricks credentials missing from .env file.")

QUERY = """
SELECT 
    DATE_TRUNC('month', date) AS month,
    MAX(value) AS production_index,
    MAX(inventory_usd) AS micron_inventory_usd,
    MAX(cycle_phase) AS cycle_phase
FROM workspace.default.industrial_production
GROUP BY DATE_TRUNC('month', date)
ORDER BY month ASC;
"""

print("Connecting to Databricks SQL Warehouse...")

with sql.connect(
    server_hostname=SERVER_HOSTNAME,
    http_path=HTTP_PATH,
    access_token=ACCESS_TOKEN,
    _tls_no_verify=True
) as connection:
    with connection.cursor() as cursor:
        print("Executing query on Databricks...")
        cursor.execute(QUERY)
        result = cursor.fetchall_arrow()
        df = result.to_pandas()

print(f"Success! Pulled {len(df)} rows from Databricks.")

# Format for Prophet and remove timezone if present
prophet_df = df[['month', 'production_index']].dropna().rename(
    columns={'month': 'ds', 'production_index': 'y'}
)

# Strip out timezone to satisfy Prophet's requirements
prophet_df['ds'] = pd.to_datetime(prophet_df['ds']).dt.tz_localize(None)

print("Training Prophet model...")
model = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
model.fit(prophet_df)

future = model.make_future_dataframe(periods=12, freq='MS')
forecast = model.predict(future)

os.makedirs("data", exist_ok=True)
forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_csv("data/semiconductor_forecast.csv", index=False)

model.plot(forecast)
plt.title("Semiconductor Production Index: Historical vs 12-Month Forecast")
plt.savefig("data/forecast_plot.png")
print("Forecast and plot saved successfully!")