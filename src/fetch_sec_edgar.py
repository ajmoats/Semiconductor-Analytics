import os
import pandas as pd
import requests as req

# SEC EDGAR requires a User-Agent header with your Name and Email
HEADERS = {
    "User-Agent": "AJ Moats alexisjmoats.com"
}

# Verified CIK dictionary (cleaned up whitespace and AMD flag)
COMPANIES = {
    "Micron Technology": "0000723125",
    "Texas Instruments": "0000097476",
    "Analog Devices": "0000006281",
    "Microchip Technology": "0000827054",
    "NVIDIA": "0001045810",
    "Intel": "0000050863",
    "AMD": "0000002488",
    "Applied Materials": "0000006951",
    "Lam Research": "0000707549",
    "KLA Corporation": "0000319201",
    "TSMC": "0001046179",
    "ASML Holding": "0000937966",
    "Samsung Electronics": "0000879316",
}

os.makedirs("data", exist_ok=True)

# Loop through each company in your dictionary
for name, cik in COMPANIES.items():
    print(f"Fetching SEC EDGAR data for {name} (CIK: {cik})...")
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    
    response = req.get(url, headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        
        try:
            # Extract US-GAAP Inventory Data
            inventory_data = data['facts']['us-gaap']['InventoryNet']['units']['USD']
            df = pd.DataFrame(inventory_data)
            
            # Filter for actual quarterly (10-Q) and annual (10-K) filings
            df = df[df['form'].isin(['10-Q', '10-K'])]
            
            # Keep relevant columns and rename for clarity
            df = df[['end', 'val']].rename(columns={'end': 'date', 'val': 'inventory_usd'})
            
            # Clean data types
            df['date'] = pd.to_datetime(df['date'])
            
            # Keep the most recent report for each date (handles restatements)
            df = df.drop_duplicates(subset=['date'], keep='last').sort_values('date')
            
            # Format filename safely (e.g., "Applied Materials" -> "applied_materials")
            safe_name = name.lower().replace(" ", "_")
            output_path = f"data/sec_{safe_name}_inventory.csv"
            df.to_csv(output_path, index=False)
            
            print(f"  -> Success! Saved {len(df)} records to '{output_path}'.")
            
        except KeyError:
            print(f"  -> Error: Could not find standard InventoryNet data for {name}.")
            
    else:
        print(f"  -> Failed to fetch data for {name}. Status code: {response.status_code}")