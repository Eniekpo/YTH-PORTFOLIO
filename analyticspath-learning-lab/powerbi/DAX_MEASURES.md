# DAX Measure Library

Assume the fact table is named `Sales`.

```DAX
Total Revenue =
SUM(Sales[Revenue])
```

```DAX
Total Profit =
SUM(Sales[Profit])
```

```DAX
Total Cost =
SUM(Sales[Cost])
```

```DAX
Orders =
DISTINCTCOUNT(Sales[Order_ID])
```

```DAX
Units Sold =
SUM(Sales[Quantity])
```

```DAX
Profit Margin =
DIVIDE([Total Profit], [Total Revenue])
```

```DAX
Average Order Value =
DIVIDE([Total Revenue], [Orders])
```

```DAX
Revenue PY =
CALCULATE(
    [Total Revenue],
    SAMEPERIODLASTYEAR('Date'[Date])
)
```

```DAX
Revenue YoY Change =
[Total Revenue] - [Revenue PY]
```

```DAX
Revenue YoY % =
DIVIDE([Revenue YoY Change], [Revenue PY])
```

```DAX
Profit PY =
CALCULATE(
    [Total Profit],
    SAMEPERIODLASTYEAR('Date'[Date])
)
```

```DAX
Profit YoY % =
DIVIDE([Total Profit] - [Profit PY], [Profit PY])
```

## Formatting

- Revenue / Profit / Cost / AOV: Currency
- Profit Margin / YoY %: Percentage
- Orders / Units Sold: Whole number
