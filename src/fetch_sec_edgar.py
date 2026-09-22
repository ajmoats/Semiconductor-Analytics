import os
import pandas as pd
import requests as req

HEADERS = {
    "User-Agent": "AJ Moats alexisjmoats.com"
}

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
    "KLA Corporation": "0000319201"
}

os.makedirs("data", exist_ok=True)
all_dfs = []

for name, cik in COMPANIES.items():
    print(f"Fetching SEC EDGAR data for {name}...")
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    response = req.get(url, headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        try:
            inventory_data = data['facts']['us-gaap']['InventoryNet']['units']['USD']
            df = pd.DataFrame(inventory_data)
            df = df[df['form'].isin(['10-Q', '10-K'])]
            df = df[['end', 'val']].rename(columns={'end': 'date', 'val': 'inventory_usd'})
            df['date'] = pd.to_datetime(df['date'])
            df = df.drop_duplicates(subset=['date'], keep='last').sort_values('date')
            
            # Tag the dataframe with the company name
            df['company'] = name
            all_dfs.append(df)
            
        except KeyError:
            print(f"  -> Could not find standard InventoryNet for {name}.")

# Combine everything into one master file with a 'company' column
if all_dfs:
    master_df = pd.concat(all_dfs, ignore_index=True)
    master_path = "data/sec_10company_inventory.csv"
    master_df.to_csv(master_path, index=False)
    print(f"Saved master dataset with company labels to '{master_path}'.")