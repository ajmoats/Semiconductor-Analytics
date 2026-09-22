import os
import pandas as pd
import requests as req

# SEC EDGAR requires a User-Agent header with your Name and Email
# Replace the email below with your actual email address
HEADERS = {
    "User-Agent": "AJ Moats alexisjmoats.com"
}

# CIK (Central Index Key) for Micron Technology. 
# SEC requires it to be exactly 10 digits, zero-padded.
CIK = "0000723125" 
URL = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json"

print("Fetching SEC EDGAR data for Micron Technology...")
response = req.get(URL, headers=HEADERS)

if response.status_code == 200:
    data = response.json()
    
    # Extract US-GAAP Inventory Data
    try:
        # SEC data is deeply nested. We target standard Inventory (Net) in USD
        inventory_data = data['facts']['us-gaap']['InventoryNet']['units']['USD']
        df = pd.DataFrame(inventory_data)
        
        # Filter for actual quarterly (10-Q) and annual (10-K) filings
        df = df[df['form'].isin(['10-Q', '10-K'])]
        
        # Keep relevant columns and rename for clarity
        df = df[['end', 'val']].rename(columns={'end': 'date', 'val': 'inventory_usd'})
        
        # Clean data types
        df['date'] = pd.to_datetime(df['date'])
        
        # Companies often restate values in later filings; keep the most recent report for each date
        df = df.drop_duplicates(subset=['date'], keep='last').sort_values('date')
        
        # Save output
        os.makedirs("data", exist_ok=True)
        output_path = "data/sec_micron_inventory.csv"
        df.to_csv(output_path, index=False)
        
        print(f"Success! Saved {len(df)} inventory records to '{output_path}'.")
        
    except KeyError:
        print("Error: Could not find standard InventoryNet data in this company's filings.")
        
else:
    print(f"Failed to fetch data from SEC. Status code: {response.status_code}")
    print(f"Response: {response.text}")