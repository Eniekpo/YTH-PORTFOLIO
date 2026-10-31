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