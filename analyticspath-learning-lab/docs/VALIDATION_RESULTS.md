# Cross-Tool Validation Reference

Use these values to verify that Excel, SQL, Python, and Power BI are using the same KPI definitions.

| KPI | Expected value |
|---|---:|
| Orders | 1,800 |
| Total Revenue | $994,444.64 |
| Total Profit | $311,406.63 |
| Profit Margin | 31.31% |
| Units Sold | 8,151 |
| Average Order Value | $552.47 |

The project keeps full calculation precision in the source model and applies currency formatting at presentation time. This avoids cross-tool differences caused by differing row-level rounding rules.

These values apply only to the synthetic training dataset.
