import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="E-Commerce Business Intelligence", page_icon="🛒", layout="wide")

BASE_DIR = Path(__file__).resolve().parent
ORDERS_FILE = BASE_DIR / "Orders.csv"
DETAILS_FILE = BASE_DIR / "Details.csv"

@st.cache_data
def load_data():
    orders = pd.read_csv(ORDERS_FILE)
    details = pd.read_csv(DETAILS_FILE)

    orders.columns = orders.columns.str.strip()
    details.columns = details.columns.str.strip()

    required_orders = {"Order ID", "Order Date", "CustomerName", "State", "City"}
    required_details = {"Order ID", "Amount", "Profit", "Quantity", "Category", "Sub-Category", "PaymentMode"}

    missing_orders = required_orders - set(orders.columns)
    missing_details = required_details - set(details.columns)
    if missing_orders or missing_details:
        raise ValueError(
            f"Missing columns. Orders.csv: {sorted(missing_orders)}; "
            f"Details.csv: {sorted(missing_details)}"
        )

    orders["Order ID"] = orders["Order ID"].astype(str).str.strip()
    details["Order ID"] = details["Order ID"].astype(str).str.strip()

    orders["Order Date"] = pd.to_datetime(orders["Order Date"], dayfirst=True, errors="coerce")
    for col in ["Amount", "Profit", "Quantity"]:
        details[col] = pd.to_numeric(details[col], errors="coerce")

    if orders["Order ID"].duplicated().any():
        # Keep one customer/location/date record per order ID.
        orders = orders.drop_duplicates(subset=["Order ID"], keep="first")

    df = details.merge(orders, on="Order ID", how="left", validate="many_to_one")
    df = df.dropna(subset=["Order ID", "Order Date", "Amount", "Profit", "Quantity"])
    df["Month"] = df["Order Date"].dt.to_period("M").astype(str)
    return orders, details, df

try:
    orders, details, df = load_data()
except Exception as exc:
    st.error(f"Could not load the dataset: {exc}")
    st.stop()

st.title("🛒 E-Commerce Sales & Business Intelligence")
st.caption("Interactive business analysis built from Orders.csv and Details.csv")

# Sidebar filters
st.sidebar.header("Filters")

date_min, date_max = df["Order Date"].min().date(), df["Order Date"].max().date()
date_range = st.sidebar.date_input("Order date", (date_min, date_max), min_value=date_min, max_value=date_max)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range

def select_filter(label, column):
    values = sorted(df[column].dropna().astype(str).unique().tolist())
    return st.sidebar.multiselect(label, values, default=values)

states = select_filter("State", "State")
cities = select_filter("City", "City")
categories = select_filter("Category", "Category")
subcats = select_filter("Sub-Category", "Sub-Category")
payments = select_filter("PaymentMode", "PaymentMode")

mask = (
    df["Order Date"].dt.date.between(start_date, end_date)
    & df["State"].astype(str).isin(states)
    & df["City"].astype(str).isin(cities)
    & df["Category"].astype(str).isin(categories)
    & df["Sub-Category"].astype(str).isin(subcats)
    & df["PaymentMode"].astype(str).isin(payments)
)
fdf = df.loc[mask].copy()

# KPIs
sales = fdf["Amount"].sum()
profit = fdf["Profit"].sum()
quantity = fdf["Quantity"].sum()
order_count = fdf["Order ID"].nunique()
customer_count = fdf["CustomerName"].nunique()
aov = fdf.groupby("Order ID")["Amount"].sum().mean() if order_count else 0
margin = profit / sales if sales else 0

k1, k2, k3, k4, k5, k6, k7 = st.columns(7)
k1.metric("Total Sales", f"₹{sales:,.0f}")
k2.metric("Total Profit", f"₹{profit:,.0f}")
k3.metric("Orders", f"{order_count:,}")
k4.metric("Quantity", f"{quantity:,}")
k5.metric("Customers", f"{customer_count:,}")
k6.metric("Avg Order Value", f"₹{aov:,.0f}")
k7.metric("Profit Margin", f"{margin:.1%}")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Executive Overview", "Sales & Products", "Customers & Geography",
    "Payments", "Business Insights"
])

with tab1:
    st.subheader("Monthly Sales and Profit")
    monthly = (
        fdf.groupby("Month", as_index=False)
        .agg(Sales=("Amount", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"))
        .sort_values("Month")
    )
    if not monthly.empty:
        fig = px.line(monthly, x="Month", y=["Sales", "Profit"], markers=True,
                      title="Monthly Sales and Profit")
        st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            cat = fdf.groupby("Category", as_index=False).agg(Sales=("Amount","sum"), Profit=("Profit","sum"))
            fig_cat = px.bar(cat, x="Category", y=["Sales","Profit"], barmode="group",
                             title="Category Performance")
            st.plotly_chart(fig_cat, use_container_width=True)
        with c2:
            st.dataframe(monthly, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Product and Category Performance")
    c1, c2 = st.columns(2)
    with c1:
        sub = (fdf.groupby("Sub-Category", as_index=False)
               .agg(Sales=("Amount","sum"), Profit=("Profit","sum"), Quantity=("Quantity","sum"))
               .sort_values("Sales", ascending=False))
        fig = px.bar(sub.head(12), x="Sales", y="Sub-Category", orientation="h",
                     title="Top Sub-Categories by Sales")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.bar(sub.sort_values("Profit").head(12), x="Profit", y="Sub-Category",
                     orientation="h", title="Lowest-Profit Sub-Categories")
        st.plotly_chart(fig, use_container_width=True)
    st.dataframe(sub, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Customer and Geographic Analysis")
    c1, c2 = st.columns(2)
    with c1:
        states_df = (fdf.groupby("State", as_index=False)
                     .agg(Sales=("Amount","sum"), Profit=("Profit","sum"), Orders=("Order ID","nunique"))
                     .sort_values("Sales", ascending=False))
        fig = px.bar(states_df.head(10), x="Sales", y="State", orientation="h",
                     title="Top States by Sales")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        cust = (fdf.groupby("CustomerName", as_index=False)
                .agg(Sales=("Amount","sum"), Profit=("Profit","sum"), Orders=("Order ID","nunique"))
                .sort_values("Sales", ascending=False))
        fig = px.bar(cust.head(10), x="Sales", y="CustomerName", orientation="h",
                     title="Top Customers by Sales")
        st.plotly_chart(fig, use_container_width=True)
    st.dataframe(states_df, use_container_width=True, hide_index=True)

with tab4:
    st.subheader("Payment Mode Analysis")
    pay = (fdf.groupby("PaymentMode", as_index=False)
           .agg(Sales=("Amount","sum"), Profit=("Profit","sum"), Orders=("Order ID","nunique"), Quantity=("Quantity","sum"))
           .sort_values("Sales", ascending=False))
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(pay, x="PaymentMode", y="Sales", title="Sales by Payment Mode")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.pie(pay, names="PaymentMode", values="Orders", title="Order Mix by Payment Mode")
        st.plotly_chart(fig, use_container_width=True)
    st.dataframe(pay, use_container_width=True, hide_index=True)

with tab5:
    st.subheader("Evidence-Based Business Insights")
    if fdf.empty:
        st.warning("No data matches the current filters.")
    else:
        cat = fdf.groupby("Category").agg(Sales=("Amount","sum"), Profit=("Profit","sum"))
        sub = fdf.groupby("Sub-Category").agg(Sales=("Amount","sum"), Profit=("Profit","sum"))
        state = fdf.groupby("State").agg(Sales=("Amount","sum"), Profit=("Profit","sum"))
        month = fdf.groupby("Month").agg(Sales=("Amount","sum"), Profit=("Profit","sum"))

        best_cat_sales = cat["Sales"].idxmax()
        best_cat_profit = cat["Profit"].idxmax()
        loss_sub = sub.sort_values("Profit").iloc[0]
        loss_sub_name = sub["Profit"].idxmin()
        loss_state_name = state["Profit"].idxmin()
        loss_month_name = month["Profit"].idxmin()

        insights = [
            (
                "Category performance",
                f"{best_cat_sales} has the highest sales among categories in the current filter.",
                f"Sales contribution is concentrated in this category.",
                "Review inventory and promotion plans for the category while monitoring its profit contribution."
            ),
            (
                "Profit driver",
                f"{best_cat_profit} generates the highest total profit among categories in the current filter.",
                "This category is an important contributor to overall profit.",
                "Protect availability of profitable sub-categories and monitor margin as sales scale."
            ),
            (
                "Profit risk",
                f"{loss_sub_name} has the lowest total profit among sub-categories in the current filter (₹{loss_sub['Profit']:,.0f}).",
                "Negative or weak contribution can reduce overall profitability even when sales exist.",
                "Review pricing, discounts, costs, or product mix for this sub-category before increasing its promotion."
            ),
            (
                "Geographic risk",
                f"{loss_state_name} has the lowest total profit among states in the current filter.",
                "A low-profit region may need a different commercial or product strategy.",
                "Investigate product mix and order economics in this state before scaling spend."
            ),
            (
                "Monthly risk",
                f"{loss_month_name} has the lowest total profit among months in the current filter.",
                "The month-level result indicates a period that deserves further investigation.",
                "Compare its category, state, and payment mix with stronger months to identify actionable differences."
            ),
        ]
        for title, finding, impact, action in insights:
            st.markdown(f"**{title}**")
            st.write(f"**Finding:** {finding}")
            st.write(f"**Business Impact:** {impact}")
            st.write(f"**Recommended Action:** {action}")
            st.divider()

st.caption("All metrics and insights are calculated dynamically from the two CSV files. The dashboard does not use machine-learning predictions.")
