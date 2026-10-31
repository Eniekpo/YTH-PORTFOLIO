import pandas as pd
from pathlib import Path

# Define project folders
DATA_FOLDER = Path("data")
OUTPUT_FOLDER = Path("output")

# Create output folder if it doesn't exist
OUTPUT_FOLDER.mkdir(exist_ok=True)

# Find all Excel files
excel_files = list(DATA_FOLDER.glob("*.xlsx"))

if not excel_files:
    raise FileNotFoundError("No Excel files found in the data folder.")

# Read and combine all files
dataframes = []

for file in excel_files:
    df = pd.read_excel(file)
    dataframes.append(df)

sales = pd.concat(dataframes, ignore_index=True)

# Clean column names
sales.columns = sales.columns.str.strip()

# Rename columns to match required schema (if needed)
column_mapping = {
    "Date": "Order_Date",
    "Region": None,  # drop Region column if present
}
# Apply renaming, dropping any columns set to None
sales = sales.rename(columns={k: v for k, v in column_mapping.items() if v})
# Drop columns that are not needed (e.g., Region)
if "Region" in sales.columns:
    sales.drop(columns=["Region"], inplace=True)

# Add Order_ID as incremental identifier
sales.insert(0, "Order_ID", range(1, len(sales) + 1))

# Define required columns in order
REQUIRED_COLUMNS = [
    "Order_ID",
    "Order_Date",
    "Product",
    "Quantity",
    "Unit_Price",
]

# Ensure required columns exist after processing
missing = [col for col in REQUIRED_COLUMNS if col not in sales.columns]
if missing:
    raise ValueError(f"Missing required columns after processing: {missing}")

# Keep only required columns
sales = sales[REQUIRED_COLUMNS]

# Remove duplicate records
sales.drop_duplicates(inplace=True)

# Remove records with missing essential values
sales.dropna(subset=REQUIRED_COLUMNS, inplace=True)

# Convert data types
sales["Order_Date"] = pd.to_datetime(sales["Order_Date"], errors="coerce")
sales["Quantity"] = pd.to_numeric(sales["Quantity"], errors="coerce")
sales["Unit_Price"] = pd.to_numeric(sales["Unit_Price"], errors="coerce")

# Remove invalid records (rows where conversion failed)
sales.dropna(subset=["Order_Date", "Quantity", "Unit_Price"], inplace=True)

# Filter out rows with non‑positive quantity or price
sales = sales[(sales["Quantity"] > 0) & (sales["Unit_Price"] >= 0)]

print("Total cleaned records:", len(sales))


# Calculate revenue
sales["Revenue"] = (
    sales["Quantity"] * sales["Unit_Price"]
)

# Summarize sales by region (if Region column exists)
if "Region" in sales.columns:
    regional_report = (
        sales.groupby("Region", as_index=False)
        .agg(
            Total_Quantity=("Quantity", "sum"),
            Total_Revenue=("Revenue", "sum"),
            Total_Transactions=("Revenue", "count")
        )
        .sort_values("Total_Revenue", ascending=False)
    )
else:
    regional_report = pd.DataFrame()

# Summarize sales by product
product_report = (
    sales.groupby("Product", as_index=False)
    .agg(
        Total_Quantity=("Quantity", "sum"),
        Total_Revenue=("Revenue", "sum")
    )
    .sort_values("Total_Revenue", ascending=False)
)

# Export all reports into one Excel workbook
output_file = OUTPUT_FOLDER / "sales_performance_report.xlsx"

with pd.ExcelWriter(
    output_file,
    engine="openpyxl"
) as writer:

    sales.to_excel(
        writer,
        sheet_name="Cleaned Sales",
        index=False
    )

    regional_report.to_excel(
        writer,
        sheet_name="Regional Performance",
        index=False
    )

    product_report.to_excel(
        writer,
        sheet_name="Product Performance",
        index=False
    )

print("Report generated successfully!")
print("Saved to:", output_file)


def format_currency_column(df, column):
    df[column] = df[column].apply(
        lambda x: f"${x:,.2f}" if pd.notna(x) else ""
    )
    return df
    