import duckdb
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data"
SQL  = ROOT / "sql"
OUTPUT_TABLES = ROOT / "outputs" / "tables"

PATHS = {
    'orders_path':       DATA / "olist_orders_dataset.csv",
    'customers_path':    DATA / "olist_customers_dataset.csv",
    'items_path':        DATA / "olist_order_items_dataset.csv",
    'payments_path':     DATA / "olist_order_payments_dataset.csv",
    'reviews_path':      DATA / "olist_order_reviews_dataset.csv",
    'products_path':     DATA / "olist_products_dataset.csv",
    'translations_path': DATA / "product_category_name_translation.csv",
}

QUERIES = {
    "funnel_analysis":  SQL / "funnel_analysis.sql",
    "segment_analysis": SQL / "segment_analysis.sql",
}


def load_query(path: Path) -> str:
    with open(path, "r") as f:
        return f.read()


def fill_paths(sql: str) -> str:
    # Replace every {placeholder} with the real forward-slash path
    filled = sql
    for key, path in PATHS.items():
        safe = str(path).replace("\\", "/")
        filled = filled.replace("{" + key + "}", safe)
    return filled


def run_query(sql: str) -> pd.DataFrame:
    con = duckdb.connect()
    result = con.execute(sql).df()
    con.close()
    return result


def main():
    print("Running SQL analyses...\n")

    for name, path in QUERIES.items():
        print(f"{'='*55}")
        print(f"  {name.upper().replace('_', ' ')}")
        print(f"{'='*55}")

        sql = fill_paths(load_query(path))

        try:
            df = run_query(sql)

            with pd.option_context(
                'display.max_rows', None,
                'display.max_columns', None,
                'display.width', None,
                'display.float_format', '{:,.2f}'.format
            ):
                print(df.to_string(index=False))

            out_path = OUTPUT_TABLES / f"{name}.csv"
            df.to_csv(out_path, index=False)
            print(f"\nSaved to {out_path}\n")

        except Exception as e:
            print(f"\nERROR in {name}: {type(e).__name__}: {e}\n")

    print("\nNow running cohort retention analysis...")
    print("(This one runs as its own Python script)\n")

    import subprocess, sys
    result = subprocess.run(
        [sys.executable, str(ROOT / "python" / "cohort_retention.py")],
        capture_output=False
    )
    if result.returncode == 0:
        print("\nCohort analysis complete.")
    else:
        print("\nCohort analysis encountered an error — check output above.")

    print(f"\n{'='*55}")
    print("All analyses complete.")
    print(f"Tables: {OUTPUT_TABLES}")
    print(f"Charts: {ROOT / 'outputs' / 'charts'}")
    print(f"{'='*55}")


if __name__ == "__main__":
    main()