# Power BI Model and Wireframe

## Minimal Model

```text
Date
  |
  | 1:*
  v
Sales
```

The supplied CSV is intentionally denormalized for the first Power BI build.

For an advanced extension, create dimensions for:
- Product
- Geography
- Salesperson
- Channel / Customer Segment

and convert the report to a star schema.

## Executive Page Wireframe

```text
+-----------------------------------------------------------+
| Revenue | Profit | Margin | Orders | Units | AOV          |
+-----------------------------------------------------------+
| Monthly Revenue Trend              | Revenue by Region    |
|                                    |                      |
+------------------------------------+----------------------+
| Revenue by Category                | Channel Performance  |
|                                    |                      |
+-----------------------------------------------------------+
| Slicers: Year | Region | Category | Channel               |
+-----------------------------------------------------------+
```
