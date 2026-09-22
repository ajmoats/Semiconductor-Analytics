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

fig, ax = plt.subplots(figsize=(12, 6))

# Plot historical actuals as black dots
ax.plot(prophet_df['ds'], prophet_df['y'], 'k.', label='Historical Production Index', alpha=0.6)

# Plot forecasted trend line (yhat)
ax.plot(forecast['ds'], forecast['yhat'], color='#1f77b4', linewidth=2, label='12-Month Trend Forecast')

# Plot uncertainty/confidence interval band (yhat_lower to yhat_upper)
ax.fill_between(
    forecast['ds'], 
    forecast['yhat_lower'], 
    forecast['yhat_upper'], 
    color='#1f77b4', 
    alpha=0.2, 
    label='80% Confidence Interval'
)

# Professional Titles and Labels
ax.set_title("U.S. Semiconductor & Electronic Component Production Index\nHistorical Trend & 12-Month Out-of-Sample Forecast", fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel("Timeline (Years)", fontsize=11, labelpad=10)
ax.set_ylabel("Production Index (2017 = 100)", fontsize=11, labelpad=10)

# Add Grid Lines for Legibility
ax.grid(True, linestyle='--', alpha=0.5)

# Add a Clean Key / Legend
ax.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.9, fontsize=10)

# Layout adjustment and save
plt.tight_layout()
os.makedirs("data", exist_ok=True)
plt.savefig("data/forecast_plot.png", dpi=300)
print("Enhanced forecast plot successfully saved to 'data/forecast_plot.png'.")