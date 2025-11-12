import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

# App Title
st.title("📈 Free Portfolio Watchlist Dashboard")

st.write(
    """
    Build your own stock watchlist, add companies, number of shares, input your profit earned, 
    and visualize your portfolio performance. All data is fetched **free** from Yahoo Finance!
    """
)

# Step 1: Input watchlist companies
st.header("1. Create Your Watchlist")

default_tickers = ["AAPL", "MSFT", "GOOGL"]
tickers = st.multiselect(
    "Select companies by ticker (add more manually):",
    options=default_tickers,
    default=default_tickers,
)

manual_input = st.text_input("Or input tickers separated by comma (e.g. TSLA,NVDA,PFE):")
if manual_input:
    tickers += [x.strip().upper() for x in manual_input.split(",") if x.strip()]
    tickers = list(set(tickers))

if not tickers:
    st.warning("Please select or input at least one ticker.")
    st.stop()

# Step 2: Input number of shares & profit earned for each company
st.header("2. Portfolio Position Details")
portfolio_data = []

for ticker in tickers:
    col1, col2, col3 = st.columns([2,2,3])
    with col1:
        shares = st.number_input(f"{ticker} - Number of Shares:", min_value=0, value=10, key=f"shares_{ticker}")
    with col2:
        profit = st.number_input(f"{ticker} - Profit Earned (€):", value=0.0, format="%.2f", key=f"profit_{ticker}")
    with col3:
        show_logo = st.checkbox(f"Show {ticker} logo", value=True, key=f"logo_{ticker}")
    portfolio_data.append({"Ticker": ticker, "Shares": shares, "Profit": profit, "Show Logo": show_logo})

portfolio_df = pd.DataFrame(portfolio_data)

# Step 3: Fetch stock prices
st.header("3. Fetching Market Data")
price_data = []
for ticker in portfolio_df["Ticker"]:
    try:
        info = yf.Ticker(ticker)
        price = info.fast_info["last_price"]
        name = info.info.get("longName", ticker)
        logo_url = info.info.get("logo_url", "")
        price_data.append({"Ticker": ticker, "Name": name, "Price": price, "Logo": logo_url})
    except Exception:
        price_data.append({"Ticker": ticker, "Name": ticker, "Price": None, "Logo": ""})

price_df = pd.DataFrame(price_data)
merged_df = pd.merge(portfolio_df, price_df, on="Ticker")
merged_df["Market Value (€)"] = merged_df["Shares"] * merged_df["Price"]
merged_df["Total Position (€)"] = merged_df["Market Value (€)"] + merged_df["Profit"]

# Step 4: Display the dashboard
st.subheader("Portfolio Table")
st.dataframe(merged_df[["Ticker", "Name", "Shares", "Price", "Profit", "Market Value (€)", "Total Position (€)"]], use_container_width=True)

# Portfolio Total Earnings (Big Icon)
total_earnings = merged_df["Total Position (€)"].sum()
st.markdown(
    f"""
    <div style='display: flex; justify-content: center; align-items: center;'>
        <span style='font-size:60px;'>💰</span>
        <span style='font-size:36px; color: green; margin-left:10px;'><b>{total_earnings:,.2f} €</b></span>
    </div>
    """,
    unsafe_allow_html=True
)
st.caption("Total Earnings = Market Value + Profits from all positions")

# Step 5: Portfolio Graphs
st.subheader("Portfolio Distribution")
fig = px.pie(
    merged_df,
    names="Ticker",
    values="Total Position (€)",
    title="Portfolio Allocation by Company",
    color_discrete_sequence=px.colors.qualitative.Pastel
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Market Value by Stock")
fig2 = px.bar(
    merged_df,
    x="Ticker",
    y="Market Value (€)",
    text="Market Value (€)",
    color="Ticker",
    title="Market Value per Stock",
)
st.plotly_chart(fig2, use_container_width=True)

# Step 6: Optional - Show logos
show_logos = st.checkbox("Show company logos below?", value=True)
if show_logos:
    for _, row in merged_df.iterrows():
        if row["Show Logo"] and row["Logo"]:
            st.image(row["Logo"], caption=row["Name"], width=100)

st.info(
    "This app is openly available for anyone to use! Data is free via Yahoo Finance (Google Finance API is currently restricted for public use in Python). "
    "Click 'Share' in Streamlit to let others use and build their own watchlists."
)
