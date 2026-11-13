# Dataset and Methods

## Fields
InvoiceNo (invoice ID; C-prefix cancellation), StockCode (SKU), Description (product label), Quantity (units; negative values may represent returns), InvoiceDate (timestamp), UnitPrice (GBP per unit), CustomerID (customer key), Country (customer country).

## Cleaning policy
Normalize names/types; parse date/numeric fields; flag cancellation invoice IDs; compute quantity × unit price; include only non-cancelled positive-quantity, positive-price lines with valid dates in positive-sales reporting. Keep unidentified customers for overall sales reporting; exclude them from customer RFM. Retain the raw workbook.

## Metric definitions and limitations
Revenue is positive transaction-line value in GBP, not a complete accounting net-sales calculation. Orders are distinct invoices. AOV = revenue / distinct invoices. Frequency = distinct invoices per customer. RFM snapshot is the day after the maximum included invoice date. Recency scores are reversed (5 is most recent); frequency and monetary quintiles score 1–5. Segment labels are heuristic, not a predictive churn model. Product costs, overhead, shipping costs and marketing costs are not provided; true profit, margin, CAC and predictive CLV cannot be derived.

## Citation
Chen, D. (2012). Online Retail II [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5CG6D. CC BY 4.0.
