# E-Commerce Sales & Business Intelligence Dashboard

## Project overview
This project analyzes e-commerce sales data to turn transaction-level information into business intelligence: KPIs, trends, product performance, customer/geographic patterns, payment behavior, risks, opportunities, and recommended actions.

## Business problem
Management needs a simple way to understand:
- What is happening to sales and profit?
- Which categories and sub-categories contribute to performance?
- Which customers and locations contribute most?
- How are payment modes distributed?
- Where are profitability risks or opportunities?
- What actions should be investigated?

## Dataset
The project uses two files:
- `Orders.csv` — order date, customer, state and city.
- `Details.csv` — amount, profit, quantity, category, sub-category and payment mode.

The two tables are joined using `Order ID`.

Original public dataset source:
https://www.kaggle.com/datasets/amitkumar209/madhav-e-commerce-sales-dataset

## Dataset validation
- Orders rows: 500
- Detail rows: 1500
- Unique orders: 500
- Missing values found: 0 in the supplied files
- Duplicate order IDs in Orders.csv: 0
- Unmatched detail Order IDs: 0
- Date range: 01 Jan 2018 to 31 Dec 2018

## Key KPIs from the supplied data
- Total Sales: ₹437,771
- Total Profit: ₹36,963
- Total Orders: 500
- Total Quantity: 5,615
- Total Customers: 336
- Average Order Value: ₹875.54
- Profit Margin: 8.44%

## Dashboard
The Streamlit application contains:
1. Executive Overview
2. Sales & Product Analysis
3. Customer & Geographic Analysis
4. Payment Analysis
5. Business Insights

Filters:
- Order Date
- State
- City
- Category
- Sub-Category
- Payment Mode

## Technologies
Python, Pandas, Plotly, Streamlit.

## Setup
1. Put `ecommerce_business_analytics.py`, `Orders.csv`, and `Details.csv` in the same folder.
2. Install dependencies:
   `pip install -r requirements.txt`
3. Start the dashboard:
   `streamlit run ecommerce_business_analytics.py`

## Business insights from the supplied dataset
- Electronics has the highest category sales: ₹166,267, about 38.0% of total sales.
- Clothing has the highest category profit: ₹13,325.
- Printers have the highest sub-category profit: ₹Printers? (see dashboard table for exact values).
- The lowest-profit sub-category is Furnishings with profit of ₹-806.
- The lowest-profit state is Rajasthan with profit of ₹-323.
- COD has the largest number of orders in the supplied data: 347 orders.
- December has negative total profit (₹-1,604); this is a period worth investigating by category and geography.

These are descriptive findings from the supplied dataset, not causal claims.

## Project files
- `ecommerce_business_analytics.py`
- `requirements.txt`
- `README.md`
- `Project_Report.docx`
- `Orders.csv`
- `Details.csv`

## Limitations
The dataset contains sales transactions for 2018 and does not include fields such as discount, cost breakdown, marketing spend, returns, delivery time, or customer demographic attributes. Therefore, the project does not claim causal explanations for profitability or customer behavior.
