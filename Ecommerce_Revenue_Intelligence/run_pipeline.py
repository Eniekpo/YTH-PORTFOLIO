import argparse
from pathlib import Path
from src.pipeline import run_pipeline
p=argparse.ArgumentParser()
p.add_argument('--input',default='data/raw/online_retail_II.xlsx')
p.add_argument('--output-dir',default='data/processed')
a=p.parse_args()
for k,v in run_pipeline(Path(a.input),Path(a.output_dir)).items(): print(k,v)
