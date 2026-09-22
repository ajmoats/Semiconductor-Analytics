import os
import pandas as pd

# Qualitative timeline based on major SIA press releases and market reports.
# Will use this presetting to annotate our forecasting charts (Shortage vs Oversupply periods).
sia_events = [
    {"date": "2020-12-01", "event": "Global chip shortage begins (Automotive & Consumer)", "cycle_phase": "Shortage"},
    {"date": "2021-08-01", "event": "SIA reports record sales, shortage peaks", "cycle_phase": "Shortage"},
    {"date": "2022-06-01", "event": "Early signs of memory market oversupply", "cycle_phase": "Oversupply"},
    {"date": "2022-11-01", "event": "SIA reports global sales decline, inventory glut", "cycle_phase": "Oversupply"},
    {"date": "2023-09-01", "event": "Market bottoms out; AI chip demand begins surging", "cycle_phase": "Recovery"},
    {"date": "2024-02-01", "event": "SIA reports strong YoY growth driven by generative AI", "cycle_phase": "Boom"}
]

print("Generating SIA qualitative timeline annotations...")

df = pd.DataFrame(sia_events)

# Convert dates to datetime objects so they align with FRED and SEC data later
df['date'] = pd.to_datetime(df['date'])

# Ensure data folder exists
os.makedirs("data", exist_ok=True)

# Save to CSV
output_path = "data/sia_timeline_annotations.csv"
df.to_csv(output_path, index=False)

print(f"Success! Saved {len(df)} qualitative SIA timeline labels to '{output_path}'.")