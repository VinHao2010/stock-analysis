# STOCKLINE - Market intelligence terminal
### Project Documentation
> Note that this is not financial advice

---

## Table of Contents
1. [What does this do?]
2. [My libraries]
3. [Page setup & CSS]
4. [Helper functions]
5. [Finance maths]
6. [Fetching data]
7. [Super cool ASCII art]
8. [Market data]
9. [Price chart]
10. [Technical indicators]
11. [Fundamentals for analysis]
12. [Volume analysis]
13. [News]
14. [Other coding notes]
15. [Other]

---

## 1. What does this do?

This is a **market intelligence terminal**. In a nutshell, this program does the following:

1. User enters stock ticker (e.g AAPL for Apple)
2. Connects to Yahoo Finance
3. Downloads the company data and news
4. Runs some simple calculations to get RSI, MACD and Bollinger Bands
5. Displays everything in, I hope, a clean and simple interface

When I mean **stock**, I mean a tiny piece of ownership of a company. This is essentially a small fraction of a company which you own and when a company does well, your share becomes worth more. When I say **ticket**, I refer to a symbol of a company on the stock market. Take my example, AAPL for Apple.

---

## 2. My libraries

```python
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import feedparser
import pyfiglet
from datetime import datetime
```
Here's what I used each of the libraries for:
| Library | What it does |
|---|---|
| `streamlit` | Turns a Python into a browser interface, adding buttons, charts and text boxes. |
| `yfinance` | Connects to Yahoo Finance and downloads data needed. The `yf` shorthand just saves typing |
| `plotly` | Creates interactive charts and graphs. Unlike matplotlib charts, Plotly charts let you hover over data points, zoom in, and pan around which is quite cool. |
| `make_subplots` | Lets you stack charts on top of each other in one chart — e.g. a price chart on top, volume bars in the middle and MACD at the bottom. |
| `pandas` | Gives you a 'dataframe' which essentailly calculates everything and stores price history data. |
| `numpy` | Maths for the numbers and super fast. `np.isnan()` used a lot to check if a number is missing/incorrect. |
| `feedparser` | Reads RSS feeds for the news function. |
| `pyfiglet` | Converts text into large super cool ASCII art on the top of the website. |
| `datetime` | Python's built in tool which is useful for tracking the last updated time. |

---

## 3. Page setup & CSS

### Main page controls
```python
st.set_page_config(
    page_title="STOCKLINE",
    page_icon="⬛",
    layout="wide",
    initial_sidebar_state="collapsed"
)
```
This is the very first Streamlit block. It must happen before anything else is displayed in the code.
 
- `page_title` — the text shown on the browser tab
- `page_icon` — the small icon on the browser tab (a black square here to symbolise a casino)
- `layout="wide"` — uses the full browser width instead of a small column
- `initial_sidebar_state="collapsed"` — hides streamlit sidebar
  
### The CSS
```python
st.markdown("""<style> ... </style>""", unsafe_allow_html=True)
```
 
**CSS** is used to make the website look nicer. However, Streamlit does not support a seperate CSS file but we can use `st.markdown()` to add just pure HTML. The `unsafe_allow_html=True` allows us to achieve this without rendering the HTML code onto the website.
 
**Key CSS functions etc:**
 
```css
@import url('https://fonts.googleapis.com/...');
```
Uses the **inter** font from google which makes the website look clean.
 
```css
background-color: #000000 !important;
```
`#000000` is black in hex colour code. `#FCCC0A` is the Neon yellow used throughout.
 
The `!important` forces this style to override any conflicting styles Streamlit tries to apply which does not look as nice.
 
```css
[data-testid="stSidebar"] { display: none !important; }
```
This uses an attribute selector to find Streamlit's sidebar element and hide it completely.
 
**CSS classes:**
 
| Class | What it makes look nice |
|---|---|
| `.mcard` | The dark cards (boxes showing numbers like Price, Market Cap etc) |
| `.mlabel` | The grey uppercase label inside each card (eg "MARKET CAP") |
| `.mval` | The large number inside each card |
| `.mval.pos` | Overrides `.mval` colour to green for + changes |
| `.mval.neg` | Overrides `.mval` colour to red for - changes |
| `.mval.yel` | Overrides `.mval` colour to Neon yellow |
| `.ascii-wrap` | The container around the ASCII art banner |
| `.ascii-art` | The ASCII text itself which uses `white-space: pre` to keep the line breaks |
| `.news-card` | News headline card |
| `.section-hdr` | The yellow titles like "● MARKET DATA" |
 
---

## 4. Helper Functions

These are just small and useful functions and are reused multiple times. I think that these saved a lot of time during the creation and hence worth putting.

### `safe()`
```python
def safe(val, fmt=None, fallback="N/A"):
    try:
        if val is None or (isinstance(val, float) and np.isnan(val)):
            return fallback
        return fmt(val) if fmt else val
    except:
        return fallback
```
This is one of the most important helper functions. If a company's data is missing, say if they don't pay dividends, then some information may not apply. For example if you try to format "None" as a price, it causes Python to crash.

How does `safe()` solve this?
- If `val` is `None`, it returns "N/A"
- If `val` is `NaN` (not a number), it also returns "N/A"
- If not, it applies the formatting and returns the result normally.

`np.isnan()` will only work on floats, so `isinstance(value, float)` helps check the type first to avoid crashes

**Examples**
```python
safe(info.get("trailingPE"), fmt_x)
# If P/E exists then return "23.5×"
# If P/E is missing then return "N/A"
```

### Formatting functiions
```python
def fmt_price(v): return f"${v:,.2f}"       #eg $182.34. Adds commas to the numbers and also shows 2dp as a float.
def fmt_large(v):                           #eg $3.01T, $182.00B
    if v >= 1e12: return f"${v/1e12:.2f}T"
    if v >= 1e9:  return f"${v/1e9:.2f}B"
    if v >= 1e6:  return f"${v/1e6:.2f}M"
    return f"${v:,.0f}"
def fmt_pct(v): return f"{v*100:.1f}%"      #eg 26.4% (x100 as it comes as a decimal from yfinance)
def fmt_x(v): return f"{v:.1f}×"            #eg 23.5× (ratios)
```

---

## 5. Finance Maths

These are the technical indicators which are implemented in this program. It reveals their patterns historically and traders use them to predict stocks.

### RSI (Relative strength index)
```python
def rsi(series, period=14):
    d = series.diff()                                                 #calculates day to day change in price in actual numbers, eg 100->105 will be +5
    g = d.where(d > 0, 0.0).ewm(com=period-1, adjust=False).mean()    #isolates gains by replacing negative values with 0
    l = (-d.where(d < 0, 0.0)).ewm(com=period-1, adjust=False).mean() #EWM (exponential weighted moving average). It gives more importance to recent days (com=period-1 when period=14 is default)
    return 100 - (100 / (1 + g/l))                                    #g = avg gain over 14 days, l = avg loss over 14 days (made positive).

    #The final formula, 100 - (100 / (1 + g/l)) outweigh gains over losses in a weighted factor
```

> What is RSI?
> RSI measures if a stock is overbought or oversold recently, formatted in a number from 0-100.
> If it's >70, it means it's overbought and the price has risen significantly.
> If it's <30, it means it's oversold and the price has fallen alot.

### MACD (Moving average convergence divergence)
```python
def macd(series, fast=12, slow=26, sig=9):
    ef = series.ewm(span=fast, adjust=False).mean() #The fast average over 12 days, reacts quickly to new price changes
    es = series.ewm(span=slow, adjust=False).mean() #The slow average over 26 days, reacts slowly as it's long
    m  = ef - es                                    #fast-slow. When +, the stock is moving up faster than it's long term. When -, it's falling
    s  = m.ewm(span=sig, adjust=False).mean()       #Signal line; a 9 day average of the MACD line acting as a trigger line
    return m, s, m - s                              #Difference between MACD and signal. When the histogram goes from - to +, it's seen as a good (bullish) signal, shown in green/red. The function returns all three to it can be displayed seperately.
```
> What is MACD?
> It compares two moving averages of a stock price (one at last 12 days) and (one at last 26 days). When the short term average rises above the long term one, the stock has 'short term momentum' - often a buy signal. When it falls below, it's often a sell signal.
>
> A moving average is just an average price over the past N days, which is recalcuated.

### Bollinger Bands 
```python
def bollinger(series, period=20, width=2):
    sma = series.rolling(period).mean()          #SMA (simple moving average). rolling(20) creates a window of 20 days and mean() takes the average of those days. The window slides forward as days move forward
    std = series.rolling(period).std()           #Measures the spread of the stock over 20 days (standard deviation). If it's high, it means the bands are wider, resulting in a more volatile stock.
    return sma + width*std, sma, sma - width*std #Upper and lower band. Returns upper band, middle band (SMA) and lower band.
```

> What are Bollinger Bands?
> Bollinger bands draw a channel around the stock price based on it's normal movement. There is a middle line (20 day avg) and teh two outer bands, showing the normal range of a stock.
> When the price touches the upper band, it's often considered high and possibly overbought. However, when it touches the lower band, it's considered low and possibly oversold. If the bands squeeze, it shows the stock has been stable.
>
> On the chart, it is showsn as a yellow envelope around the candles.

### `rsi_label()` - The RSI number
```python
def rsi_label(v):
    if v >= 70: return "OVERBOUGHT", "#FF453A"   #red
    if v <= 30: return "OVERSOLD",   "#30D158"   #green
    return "NEUTRAL", "#FCCC0A"                  #yellow
```
Classification function that returns a text label and number to the UI, returned as tuple.

---

## 6. Fetching data

```python
symbol = ticker_input.strip().upper()                  #removes accidental spaces when ticker typed, converted to upper case as per yfinance needs
                               
with st.spinner(f"LOADING  {symbol} ..."):             #loading animation 
    tk   = yf.Ticker(symbol)                           #creates a ticker object that is supposed to communicated with yfinance about a specific company
    info = tk.info                                     #dictionary that contains the data points about the company (price, market cap, P/E ratio, address, sector etc in ONE request to yfinance)
    hist = tk.history(period=period, auto_adjust=True) #donwloads historical daily price data as pandas dataframe where each row is a day. colums are open, high, low, close, vol.
#period is selected by user, and auto_adjust adjusts the prices for stock splits and dividends 
```

