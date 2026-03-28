import duckdb
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

con = duckdb.connect()

# The tables we need to understand
files = {
    "orders":       "data/olist_orders_dataset.csv",
    "customers":    "data/olist_customers_dataset.csv",
    "order_items":  "data/olist_order_items_dataset.csv",
    "payments":     "data/olist_order_payments_dataset.csv",
    "reviews":      "data/olist_order_reviews_dataset.csv",
    "products":     "data/olist_products_dataset.csv",
    "translations": "data/product_category_name_translation.csv",
}

for name, path in files.items():
    print("\n" + "="*60)
    print(f"TABLE: {name}")
    print("="*60)

    # Shape and columns
    df = con.execute(f"""
        SELECT * FROM read_csv_auto('{path}') LIMIT 3
    """).df()

    full_count = con.execute(f"""
        SELECT COUNT(*) as row_count FROM read_csv_auto('{path}')
    """).fetchone()[0]

    print(f"Rows: {full_count}")
    print(f"Columns: {list(df.columns)}")
    print(f"\nSample (3 rows):")
    print(df.to_string(index=False))

# One extra check: order status breakdown
# This tells us what funnel stages actually exist in the data
print("\n" + "="*60)
print("ORDER STATUS BREAKDOWN")
print("="*60)
status = con.execute("""
    SELECT
        order_status,
        COUNT(*) as count,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as pct
    FROM read_csv_auto('data/olist_orders_dataset.csv')
    GROUP BY order_status
    ORDER BY count DESC
""").df()
print(status.to_string(index=False))

# Date range of the dataset
print("\n" + "="*60)
print("DATE RANGE")
print("="*60)
dates = con.execute("""
    SELECT
        MIN(order_purchase_timestamp) as earliest_order,
        MAX(order_purchase_timestamp) as latest_order
    FROM read_csv_auto('data/olist_orders_dataset.csv')
""").df()
print(dates.to_string(index=False))

con.close()