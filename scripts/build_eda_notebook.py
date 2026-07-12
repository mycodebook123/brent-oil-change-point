import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []

cells.append(nbf.v4.new_markdown_cell(
"""# Task 1 & 2: Brent Oil Price - Data Preparation and Exploratory Data Analysis

**Birhan Energies - Change Point Analysis Project**

This notebook covers:
1. Data loading and preprocessing
2. Time series visualization
3. Log returns calculation
4. Stationarity testing (ADF)
5. Volatility pattern analysis
"""))

cells.append(nbf.v4.new_code_cell(
"""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from statsmodels.tsa.stattools import adfuller

plt.style.use('seaborn-v0_8-darkgrid')
%matplotlib inline
"""))

cells.append(nbf.v4.new_markdown_cell("## 1. Load and Prepare Data"))

cells.append(nbf.v4.new_code_cell(
"""df = pd.read_csv('../data/BrentOilPrices.csv')
df['Date'] = pd.to_datetime(df['Date'], format='mixed')
df = df.sort_values('Date').reset_index(drop=True)

print(f"Shape: {df.shape}")
print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
df.head()
"""))

cells.append(nbf.v4.new_code_cell(
"""df.describe()
"""))

cells.append(nbf.v4.new_markdown_cell("## 2. Load Events Data"))

cells.append(nbf.v4.new_code_cell(
"""events = pd.read_csv('../data/events.csv')
events['Date'] = pd.to_datetime(events['Date'])
print(f"Number of events: {len(events)}")
events
"""))

cells.append(nbf.v4.new_markdown_cell("## 3. Raw Price Series"))

cells.append(nbf.v4.new_code_cell(
"""fig, ax = plt.subplots(figsize=(16, 6))
ax.plot(df['Date'], df['Price'], linewidth=0.8, color='#1f4e79')
ax.set_title('Brent Oil Price (1987-2022)', fontsize=14, fontweight='bold')
ax.set_xlabel('Date')
ax.set_ylabel('Price (USD/barrel)')
ax.xaxis.set_major_locator(mdates.YearLocator(5))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.tight_layout()
plt.savefig('../data/raw_price_series.png', dpi=150)
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(
"""**Observations to note here:** look for long-run trend direction, the major spikes/crashes (1990, 2008, 2014-16, 2020, 2022), and whether volatility looks constant or clustered over time. Fill in your written observations after running this cell."""))

cells.append(nbf.v4.new_markdown_cell("## 4. Log Returns"))

cells.append(nbf.v4.new_code_cell(
"""df['LogPrice'] = np.log(df['Price'])
df['LogReturn'] = df['LogPrice'].diff()
df_returns = df.dropna(subset=['LogReturn']).reset_index(drop=True)

df_returns[['Date', 'Price', 'LogReturn']].head()
"""))

cells.append(nbf.v4.new_code_cell(
"""fig, ax = plt.subplots(figsize=(16, 5))
ax.plot(df_returns['Date'], df_returns['LogReturn'], linewidth=0.5, color='#a63603')
ax.set_title('Brent Oil Log Returns (Daily)', fontsize=14, fontweight='bold')
ax.set_xlabel('Date')
ax.set_ylabel('Log Return')
ax.xaxis.set_major_locator(mdates.YearLocator(5))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.tight_layout()
plt.savefig('../data/log_returns.png', dpi=150)
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(
"""**Volatility clustering:** note the visibly wider bands of log returns around 2008-09, 2014-16, and 2020 — periods of high volatility clustered together, a classic sign of GARCH-type behavior in financial time series."""))

cells.append(nbf.v4.new_markdown_cell("## 5. Stationarity Testing (Augmented Dickey-Fuller)"))

cells.append(nbf.v4.new_code_cell(
"""def adf_report(series, name):
    result = adfuller(series.dropna())
    print(f"--- ADF Test: {name} ---")
    print(f"ADF Statistic: {result[0]:.4f}")
    print(f"p-value: {result[1]:.4f}")
    print(f"Critical Values: {result[4]}")
    if result[1] < 0.05:
        print(">> Stationary (reject H0 of unit root)")
    else:
        print(">> Non-stationary (fail to reject H0 of unit root)")
    print()

adf_report(df['Price'], 'Raw Price')
adf_report(df_returns['LogReturn'], 'Log Returns')
"""))

cells.append(nbf.v4.new_markdown_cell(
"""**Expected result:** the raw price series is typically non-stationary (has a unit root / trends over time), while log returns are typically stationary. This matters directly for change point modeling: a Bayesian change point model assumes a well-behaved (ideally stationary) generative process for its likelihood, so log returns — not raw prices — are the more defensible input for Task 2's PyMC model. We'll carry both forward but lean on log returns for the formal model."""))

cells.append(nbf.v4.new_markdown_cell("## 6. Rolling Volatility"))

cells.append(nbf.v4.new_code_cell(
"""df_returns['RollingVol'] = df_returns['LogReturn'].rolling(window=30).std()

fig, ax = plt.subplots(figsize=(16, 5))
ax.plot(df_returns['Date'], df_returns['RollingVol'], linewidth=0.8, color='#238b45')
ax.set_title('30-Day Rolling Volatility of Log Returns', fontsize=14, fontweight='bold')
ax.set_xlabel('Date')
ax.set_ylabel('Rolling Std Dev')
ax.xaxis.set_major_locator(mdates.YearLocator(5))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.tight_layout()
plt.savefig('../data/rolling_volatility.png', dpi=150)
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell("## 7. Save Processed Data for Task 2"))

cells.append(nbf.v4.new_code_cell(
"""df.to_csv('../data/processed_brent_prices.csv', index=False)
print("Saved processed_brent_prices.csv")
"""))

nb['cells'] = cells
nbf.write(nb, 'notebooks/01_eda.ipynb')
print("Notebook created at notebooks/01_eda.ipynb")
