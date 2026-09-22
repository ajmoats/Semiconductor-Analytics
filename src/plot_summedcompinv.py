import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load master CSV
df = pd.read_csv("data/sec_10company_inventory.csv")
df['date'] = pd.to_datetime(df['date'])

# Set up the plotting canvas
plt.figure(figsize=(14, 7))
sns.lineplot(data=df, x='date', y='inventory_usd', hue='company', marker='o', linewidth=2)

# Format titles and labels
plt.title("Semiconductor Sector Inventory Trends Over Time", fontsize=14, fontweight='bold')
plt.xlabel("Filing Date", fontsize=12)
plt.ylabel("Inventory Value (USD)", fontsize=12)

# Move the legend outside the plot area so it doesn't overlap lines
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title="Companies")
plt.tight_layout()

# Save the plot as a PNG file
os.makedirs("data", exist_ok=True)
output_img_path = "data/semiconductor_inventory_trends.png"
plt.savefig(output_img_path, dpi=300, bbox_inches='tight')

print(f"Success! Plot saved to '{output_img_path}'.")

# Close the plot to free memory
plt.close()