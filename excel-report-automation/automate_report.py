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

# Define required columns
REQUIRED_COLUMNS = [
    "Order_ID",
    "Order_Date",
    "Product",
    "Quantity",
    "Unit_Price"
]

# Ensure required columns exist
missing = [col for col in REQUIRED_COLUMNS if col not in sales.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")

# Keep only required columns in the specified order
sales = sales[REQUIRED_COLUMNS]

# Remove duplicate records
sales.drop_duplicates(inplace=True)

# Remove records with missing essential values
sales.dropna(
    subset=["Date", "Region", "Product", "Quantity", "Unit_Price"],
    inplace=True
)

# Convert data types
sales["Date"] = pd.to_datetime(sales["Date"], errors="coerce")
sales["Quantity"] = pd.to_numeric(
    sales["Quantity"], errors="coerce"
)
sales["Unit_Price"] = pd.to_numeric(
    sales["Unit_Price"], errors="coerce"
)

# Remove invalid records
sales.dropna(
    subset=["Date", "Quantity", "Unit_Price"],
    inplace=True
)

sales = sales[
    (sales["Quantity"] > 0) &
    (sales["Unit_Price"] >= 0)
]

print("Total cleaned records:", len(sales))


# Calculate revenue
sales["Revenue"] = (
    sales["Quantity"] * sales["Unit_Price"]
)

# Summarize sales by region
regional_report = (
    sales.groupby("Region", as_index=False)
    .agg(
        Total_Quantity=("Quantity", "sum"),
        Total_Revenue=("Revenue", "sum"),
        Total_Transactions=("Revenue", "count")
    )
    .sort_values("Total_Revenue", ascending=False)
)

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
    