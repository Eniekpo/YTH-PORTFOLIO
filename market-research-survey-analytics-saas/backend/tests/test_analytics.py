import pandas as pd
from app.analytics import overview, frequency, crosstab, numeric_summary, correlation_matrix

def sample_df():
    return pd.DataFrame({"gender":["F","M","F","F"],"plan":["A","A","B","B"],"score":[4,3,5,4],"spend":[10.0,20.0,30.0,40.0]})

def test_overview():
    o=overview(sample_df()); assert o["rows"]==4 and o["columns"]==4 and o["completeness_pct"]==100

def test_frequency():
    f=frequency(sample_df(),"gender"); assert f[0]["value"]=="F" and f[0]["count"]==3

def test_crosstab():
    c=crosstab(sample_df(),"gender","plan"); assert c["row_variable"]=="gender" and len(c["rows"])==2

def test_numeric_summary():
    n=numeric_summary(sample_df(),"score"); assert n["median"]==4.0

def test_correlation():
    c=correlation_matrix(sample_df()); assert set(c["columns"])=={"score","spend"}
