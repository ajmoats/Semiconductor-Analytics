import duckdb

# Query your CSV file directly using standard SQL
query = """
    SELECT company, date, inventory_usd
    FROM 'data/sec_10company_inventory.csv'
    WHERE company IN ('NVIDIA', 'AMD', 'Micron Technology')
    ORDER BY date DESC
"""

result_df = duckdb.sql(query).df()
print(result_df.head(15))