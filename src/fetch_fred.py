import os
import pandas as pd
import requests as req
from dotenv import load_dotenv

# Load an API key from the .env file
# FRED: Rederal Reserve Economic Data for Industrial Production
load_dotenv()
FRED_API_KEY = os.getenv("FRED_API_KEY")

if not FRED_API_KEY:
    raise ValueError("FRED_API_KEY not found in .env file. Please check your .env configuration.")

# Series ID for Industrial Production: Semiconductors and Other Electronic Component (IPG334411S)
SERIES_ID = "IPB53122S" # January 1965 - August 2026 Dataset
url = "https://api.stlouisfed.org/fred/series/observations"

params = {
    "series_id": SERIES_ID,
    "api_key": FRED_API_KEY,
    "file_type": "json"
}

# Internal fetching check
print("Fetching data from FRED API...")
response = req.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    observations = data.get("observations", [])
    
    # Convert to DataFrame
    df = pd.DataFrame(observations)
    
    # Convert 'date' column to datetime and 'value' column to numeric
    df['date'] = pd.to_datetime(df['date'])
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df.dropna(inplace=True)  # Drop rows with NaN values in 'value'
    
    # Ensure data folder exists & save to CSV
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/industrial_production.csv", index=False)
    print("Data fetched and saved to 'data/industrial_production.csv'.")
    
else:
    print(f"Failed to fetch data from FRED API. Status code: {response.status_code}")
    print(f"Response: {response.text}")