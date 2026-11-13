from pathlib import Path
from urllib.request import urlretrieve
URL="https://archive.ics.uci.edu/ml/machine-learning-databases/00502/online_retail_II.xlsx"
DEST=Path("data/raw/online_retail_II.xlsx")
if not DEST.exists():
    DEST.parent.mkdir(parents=True,exist_ok=True)
    print("Downloading Online Retail II from UCI...")
    urlretrieve(URL,DEST)
print(f"Dataset: {DEST} ({DEST.stat().st_size:,} bytes)")
