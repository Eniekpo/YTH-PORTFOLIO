# Power BI Build Guide

## Objective

Build a management-facing sales performance report from the same dataset already used in Excel, SQL, and Python.

## Data Source

Import:

```text
data/powerbi/retail_sales_powerbi.csv
```

## Recommended Report Pages

### Page 1: Executive Overview
Include:
- Total Revenue
- Total Profit
- Profit Margin
- Orders
- Units Sold
- Average Order Value
- Monthly revenue trend
- Revenue by Region
- Revenue by Category

### Page 2: Product & Channel Performance
Include:
- top products by revenue
- revenue and profit by category
- channel comparison
- discount-level comparison
- product drill-down

### Page 3: Customer & Sales Performance
Include:
- customer segment comparison
- salesperson leaderboard
- region → city drill-down
- segment/channel matrix

## Power Query Checks

1. Set `Order_Date` to Date.
2. Set currency fields to Decimal Number.
3. Set `Quantity` and `Year` to Whole Number.
4. Set `Discount` and `Profit_Margin` to Decimal Number / Percentage.
5. Check nulls and duplicates.
6. Keep `Order_ID` unique.

## Date Table

```DAX
Date =
ADDCOLUMNS(
    CALENDAR(MIN(Sales[Order_Date]), MAX(Sales[Order_Date])),
    "Year", YEAR([Date]),
    "Month Number", MONTH([Date]),
    "Month", FORMAT([Date], "MMMM"),
    "Year Month", FORMAT([Date], "YYYY-MM")
)
```

Create:

```text
Date[Date] 1 ──── * Sales[Order_Date]
```

Mark `Date` as a Date Table.

## Suggested Slicers

- Year
- Region
- Category
- Channel

## Validation

Before considering the report complete:
1. compare Total Revenue against the Excel dashboard;
2. compare Region totals against SQL Query 3;
3. compare Category totals against the Python notebook;
4. verify filters behave consistently.

This cross-tool reconciliation is part of the portfolio story.
