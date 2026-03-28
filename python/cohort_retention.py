import duckdb
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data"
OUTPUT_CHARTS = ROOT / "outputs" / "charts"
OUTPUT_TABLES = ROOT / "outputs" / "tables"

con = duckdb.connect()

raw = con.execute(f"""
    SELECT
        c.customer_unique_id,

        STRFTIME(
            CAST(o.order_purchase_timestamp AS TIMESTAMP),
            '%Y-%m'
        ) AS order_month

    FROM read_csv_auto('{DATA}/olist_orders_dataset.csv') o
    LEFT JOIN read_csv_auto('{DATA}/olist_customers_dataset.csv') c
        ON o.customer_id = c.customer_id

    -- Filter for 'delivered' to exclude returns/cancellations from retention metrics
    WHERE o.order_status = 'delivered'
      AND o.order_purchase_timestamp IS NOT NULL
""").df()

con.close()

print(f"Raw rows pulled: {len(raw)}")
print(raw.head())


# For each unique customer, find the earliest order month
cohort_map = (
    raw.groupby('customer_unique_id')['order_month']
    .min()
    .reset_index()
    .rename(columns={'order_month': 'cohort_month'})
)

df = raw.merge(cohort_map, on='customer_unique_id')

print(f"\nAfter cohort mapping: {len(df)} rows")
print(df.head())


df['order_period']  = pd.to_datetime(df['order_month']).dt.to_period('M')
df['cohort_period'] = pd.to_datetime(df['cohort_month']).dt.to_period('M')

# Cohort index 0 = first purchase month, 1 = one month later, etc.
df['cohort_index'] = (
    df['order_period'] - df['cohort_period']
).apply(lambda x: x.n)

print(f"\nCohort index range: {df['cohort_index'].min()} to {df['cohort_index'].max()}")


cohort_table = (
    df.groupby(['cohort_month', 'cohort_index'])['customer_unique_id']
    .nunique()
    .reset_index()
    .rename(columns={'customer_unique_id': 'customers'})
)

# Pivot: cohort_month as rows, cohort_index as columns
cohort_pivot = cohort_table.pivot_table(
    index='cohort_month',
    columns='cohort_index',
    values='customers'
)


cohort_sizes = cohort_pivot[0]  # column 0 = cohort size at month 0

retention = cohort_pivot.divide(cohort_sizes, axis=0).round(3)

print("\nRetention table (first 6 cohorts, first 6 months):")
print(retention.iloc[:6, :6])

cohort_pivot.to_csv(OUTPUT_TABLES / "cohort_counts.csv")
retention.to_csv(OUTPUT_TABLES / "cohort_retention.csv")
print(f"\nTables saved to {OUTPUT_TABLES}")


# Limit to first 12 months of retention (after that cohorts get tiny)
retention_plot = retention.iloc[:, :12]

fig, ax = plt.subplots(figsize=(14, 8))

sns.heatmap(
    retention_plot,
    annot=True,
    fmt='.0%',
    cmap='YlOrRd_r',           # green = high retention, red = low
    vmin=0,
    vmax=0.15,                 # cap at 15% — Olist retention is low
    linewidths=0.5,
    ax=ax,
    cbar_kws={'label': 'Retention Rate'}
)

ax.set_title(
    'Olist Customer Cohort Retention\n'
    'Share of customers who made another purchase N months after first order',
    fontsize=13,
    pad=15
)
ax.set_xlabel('Months Since First Purchase', fontsize=11)
ax.set_ylabel('Acquisition Cohort (Month)', fontsize=11)
ax.tick_params(axis='y', rotation=0)

plt.tight_layout()
plt.savefig(OUTPUT_CHARTS / "cohort_retention_heatmap.png", dpi=150)
plt.close()
print(f"Heatmap saved to {OUTPUT_CHARTS / 'cohort_retention_heatmap.png'}")

# Average Retention Curve
# Excluded Month 0 (100%) to see the detail of months 1-12
plot_data = retention.iloc[:, 1:13].mean()
plot_data.index = range(1, 13)

plt.figure(figsize=(12, 7))
ax = plot_data.plot(kind='line', marker='o', color='#2c3e50', linewidth=2.5, markersize=8)

for x, y in enumerate(plot_data, start=1):
    plt.text(x, y + 0.0008, f'{y:.2%}', 
             ha='center', va='bottom', 
             fontsize=10, fontweight='bold', color='#34495e')

plt.ylim(0, 0.01) 

plt.title('Average Customer Retention Curve (Excluding Month 0)', 
          fontsize=16, pad=30)
plt.ylabel('Average % of Returning Customers', fontsize=12, labelpad=10)
plt.xlabel('Months Since First Purchase', fontsize=12, labelpad=10)
plt.grid(True, axis='y', linestyle='--', alpha=0.3)

ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig(OUTPUT_CHARTS / "retention_curve.png", dpi=150)
plt.close()

print(f"Retention Curve saved to {OUTPUT_CHARTS}")