'''
PLEASE DO NOT LOOK AT THIS CODE TO GAIN AN UNDERSTANDING OF HOW IT WORKS; I urge you to read to documentation instead.

Credit is where credit is due,
Claude helped me a lot with this
'''



import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import feedparser
import pyfiglet
from datetime import datetime

#page config
st.set_page_config(
    page_title="STOCKLINE",
    page_icon="⬛",
    layout="wide",
    initial_sidebar_state="collapsed"
)

#css (w claude) - going for a apple/nyc simple font with a black/yellow sort of thing
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&display=swap');

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: #000000 !important;
    color: #FFFFFF !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', sans-serif;
}
[data-testid="stSidebar"], [data-testid="stHeader"], footer, #MainMenu { display: none !important; }
[data-testid="block-container"] { padding: 2rem 2.5rem 2rem 2.5rem !important; }

/* Input */
.stTextInput > div > div > input {
    background-color: #111111 !important;
    color: #FCCC0A !important;
    border: 2px solid #FCCC0A !important;
    border-radius: 0px !important;
    font-size: 1.4rem !important;
    font-weight: 800 !important;
    text-transform: uppercase !important;
    letter-spacing: 6px !important;
    padding: 14px 24px !important;
    caret-color: #FCCC0A;
}
.stTextInput > div > div > input::placeholder { color: #3A3A3C !important; letter-spacing: 4px; }
.stTextInput > div > div > input:focus {
    box-shadow: 0 0 0 2px rgba(252,204,10,0.25) !important;
    border-color: #FCCC0A !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background-color: #111111 !important;
    border: 1px solid #2C2C2E !important;
    border-radius: 0px !important;
    color: #FFFFFF !important;
}

/* Plotly chart container */
.stPlotlyChart { background: transparent !important; }
[data-testid="stPlotlyChart"] > div { background: transparent !important; }

/* Section headers */
.section-hdr {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 5px;
    text-transform: uppercase;
    color: #FCCC0A;
    border-bottom: 1px solid #FCCC0A;
    padding-bottom: 10px;
    margin: 36px 0 18px 0;
}

/* Metric card */
.mcard {
    background: #111111;
    border: 1px solid #1C1C1E;
    padding: 18px 20px 14px 20px;
    margin-bottom: 10px;
}
.mlabel {
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #636366;
    margin-bottom: 8px;
}
.mval { font-size: 1.6rem; font-weight: 800; color: #FFFFFF; line-height: 1; }
.mval.pos { color: #30D158; }
.mval.neg { color: #FF453A; }
.mval.yel { color: #FCCC0A; }
.mval.blu { color: #0A84FF; }
.msub { font-size: 0.7rem; color: #636366; margin-top: 5px; letter-spacing: 1px; }

/* ASCII block */
.ascii-wrap {
    background: #000;
    border-top: 2px solid #FCCC0A;
    border-bottom: 2px solid #FCCC0A;
    padding: 28px 20px 20px 20px;
    text-align: center;
    margin: 24px 0 8px 0;
    overflow-x: auto;
}
.ascii-art {
    font-family: 'Courier New', Courier, monospace;
    font-size: 0.55rem;
    line-height: 1.2;
    color: #FCCC0A;
    white-space: pre;
    display: inline-block;
    text-align: left;
}
.company-name-big {
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 10px;
    color: #FFFFFF;
    text-transform: uppercase;
    margin-top: 14px;
}
.company-meta {
    font-size: 0.6rem;
    letter-spacing: 3px;
    color: #3A3A3C;
    text-transform: uppercase;
    margin-top: 6px;
}

/* News */
.news-card {
    background: #0A0A0A;
    border-left: 3px solid #FCCC0A;
    padding: 16px 20px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: background 0.15s;
}
.news-card:hover { background: #111111; }
.news-num {
    background: #FCCC0A;
    color: #000;
    font-weight: 900;
    font-size: 0.75rem;
    width: 24px; height: 24px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center; justify-content: center;
    margin-right: 12px;
    flex-shrink: 0;
}
.news-title { font-size: 0.9rem; font-weight: 600; color: #E5E5EA; line-height: 1.45; }
.news-meta { font-size: 0.65rem; letter-spacing: 2px; color: #636366; text-transform: uppercase; margin-top: 5px; }
.news-summary { font-size: 0.78rem; color: #48484A; margin-top: 6px; line-height: 1.5; }

/* Row table */
.row-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 11px 0;
    border-bottom: 1px solid #1C1C1E;
    font-size: 0.82rem;
}
.row-key { color: #636366; }
.row-val { font-weight: 600; }

/* Ticker badge */
.ticker-badge {
    background: #FCCC0A;
    color: #000;
    font-weight: 900;
    font-size: 0.75rem;
    padding: 4px 10px;
    letter-spacing: 2px;
}

/* Spinner override */
[data-testid="stSpinner"] p { color: #FCCC0A !important; letter-spacing: 3px; }

/* Column padding */
[data-testid="column"] { padding: 0 5px !important; }
</style>
""", unsafe_allow_html=True)


# ─── HELPERS ──────────────────────────────────────────────────────────────────
def safe(val, fmt=None, fallback="N/A"):
    try:
        if val is None or (isinstance(val, float) and np.isnan(val)):
            return fallback
        return fmt(val) if fmt else val
    except:
        return fallback

def fmt_price(v): return f"${v:,.2f}"
def fmt_large(v):
    if v >= 1e12: return f"${v/1e12:.2f}T"
    if v >= 1e9:  return f"${v/1e9:.2f}B"
    if v >= 1e6:  return f"${v/1e6:.2f}M"
    return f"${v:,.0f}"
def fmt_pct(v): return f"{v*100:.1f}%"
def fmt_x(v): return f"{v:.1f}×"

def rsi(series, period=14):
    d = series.diff()
    g = d.where(d > 0, 0.0).ewm(com=period-1, adjust=False).mean()
    l = (-d.where(d < 0, 0.0)).ewm(com=period-1, adjust=False).mean()
    return 100 - (100 / (1 + g/l))

def macd(series, fast=12, slow=26, sig=9):
    ef = series.ewm(span=fast, adjust=False).mean()
    es = series.ewm(span=slow, adjust=False).mean()
    m  = ef - es
    s  = m.ewm(span=sig, adjust=False).mean()
    return m, s, m - s

def bollinger(series, period=20, width=2):
    sma = series.rolling(period).mean()
    std = series.rolling(period).std()
    return sma + width*std, sma, sma - width*std

def rsi_label(v):
    if v >= 70: return "OVERBOUGHT", "#FF453A"
    if v <= 30: return "OVERSOLD",   "#30D158"
    return "NEUTRAL", "#FCCC0A"

def get_news(symbol):
    try:
        url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
        feed = feedparser.parse(url)
        items = []
        for e in feed.entries[:5]:
            try:
                from email.utils import parsedate_to_datetime
                dt = parsedate_to_datetime(e.published).strftime("%b %d, %Y · %H:%M")
            except:
                dt = e.get("published", "")[:20]
            items.append({
                "title":   e.title,
                "date":    dt,
                "link":    e.link,
                "summary": e.get("summary", "")[:220],
            })
        return items
    except:
        return []

def ascii_art(text):
    for font in ["roman", "starwars", "larry3d", "big", "standard"]:
        try:
            art = pyfiglet.figlet_format(text, font=font)
            if art.strip():
                return art
        except:
            continue
    return text


#header
st.markdown("""
<div style="display:flex;align-items:center;gap:18px;padding-bottom:20px;border-bottom:1px solid #1C1C1E;margin-bottom:28px;">
    <div style="background:#FCCC0A;color:#000;font-weight:900;font-size:1.2rem;
                width:46px;height:46px;border-radius:50%;display:flex;
                align-items:center;justify-content:center;flex-shrink:0;">S</div>
    <div>
        <div style="font-size:2rem;font-weight:900;letter-spacing:-1px;line-height:1;">STOCKLINE</div>
        <div style="font-size:0.6rem;letter-spacing:5px;color:#FCCC0A;text-transform:uppercase;
                    margin-top:3px;">— Market Intelligence Terminal —</div>
    </div>
</div>
""", unsafe_allow_html=True)

#search
c1, c2 = st.columns([4, 1])
with c1:
    ticker_input = st.text_input("", placeholder="TICKER  →  AAPL  /  NVDA  /  TSLA",
                                  label_visibility="collapsed")
with c2:
    period = st.selectbox("", ["1mo","3mo","6mo","1y","2y","5y"],
                           index=3, label_visibility="collapsed")

#landing
if not ticker_input:
    st.markdown("""
    <div style="text-align:center;padding:100px 0 80px 0;">
        <div style="font-size:4.5rem;font-weight:900;letter-spacing:-3px;line-height:0.95;color:#1C1C1E;">
            ENTER A<br><span style="color:#FCCC0A;">TICKER</span><br>ABOVE ↑
        </div>
        <div style="margin-top:36px;font-size:0.65rem;letter-spacing:5px;color:#2C2C2E;">
            AAPL &nbsp;·&nbsp; MSFT &nbsp;·&nbsp; NVDA &nbsp;·&nbsp; TSLA &nbsp;·&nbsp; AMZN &nbsp;·&nbsp; META &nbsp;·&nbsp; GOOGL
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

#load the data (i love u yfinance)
symbol = ticker_input.strip().upper()

with st.spinner(f"LOADING  {symbol} ..."):
    tk   = yf.Ticker(symbol)
    info = tk.info
    hist = tk.history(period=period, auto_adjust=True)

if hist.empty:
    st.error(f"❌  '{symbol}' not found — check the ticker and try again.")
    st.stop()

#core prices
cur_price  = safe(info.get("currentPrice") or info.get("regularMarketPrice"), fmt_price)
raw_price  = info.get("currentPrice") or info.get("regularMarketPrice") or hist["Close"].iloc[-1]
raw_prev   = info.get("previousClose") or hist["Close"].iloc[-2] if len(hist) > 1 else raw_price
chg_abs    = raw_price - raw_prev
chg_pct    = (chg_abs / raw_prev * 100) if raw_prev else 0
chg_arrow  = "▲" if chg_abs >= 0 else "▼"
chg_cls    = "pos" if chg_abs >= 0 else "neg"

company    = info.get("longName") or info.get("shortName") or symbol
exchange   = info.get("exchange", "")
sector     = info.get("sector", "")
industry   = info.get("industry", "")

#super tuff ascii art that i definitely did not copy from the internet
art = ascii_art(symbol)
meta_parts = " · ".join(filter(None, [exchange, sector, industry]))

st.markdown(f"""
<div class="ascii-wrap">
    <div class="ascii-art">{art}</div>
    <div class="company-name-big">{company.upper()}</div>
    <div class="company-meta">{meta_parts}</div>
</div>
""", unsafe_allow_html=True)

#important indicators etc
st.markdown('<div class="section-hdr">● MARKET DATA</div>', unsafe_allow_html=True)

mkt_cap  = info.get("marketCap")
pe       = info.get("trailingPE")
fwd_pe   = info.get("forwardPE")
hi52     = info.get("fiftyTwoWeekHigh")
lo52     = info.get("fiftyTwoWeekLow")

cols = st.columns(6)
row1 = [
    ("PRICE",        fmt_price(raw_price),             "yel"),
    ("DAILY CHANGE", f"{chg_arrow} {abs(chg_pct):.2f}%\n${abs(chg_abs):.2f}", chg_cls),
    ("MARKET CAP",   safe(mkt_cap, fmt_large),          ""),
    ("P/E  (TTM)",   safe(pe, fmt_x),                   ""),
    ("52W HIGH",     safe(hi52, fmt_price),              "pos"),
    ("52W LOW",      safe(lo52, fmt_price),              "neg"),
]
for col, (lbl, val, cls) in zip(cols, row1):
    with col:
        lines = val.split("\n")
        sub = f'<div class="msub">{lines[1]}</div>' if len(lines) > 1 else ""
        st.markdown(f"""
        <div class="mcard">
            <div class="mlabel">{lbl}</div>
            <div class="mval {cls}">{lines[0]}</div>{sub}
        </div>""", unsafe_allow_html=True)

#row2
eps       = info.get("trailingEps")
div_yield = info.get("dividendYield")
beta      = info.get("beta")
margin    = info.get("profitMargins")
revenue   = info.get("totalRevenue")
debt_eq   = info.get("debtToEquity")

cols2 = st.columns(6)
row2 = [
    ("FWD  P/E",       safe(fwd_pe, fmt_x),                 ""),
    ("EPS  (TTM)",     safe(eps,    lambda v: f"${v:.2f}"),  ""),
    ("DIVIDEND YIELD", safe(div_yield, lambda v: f"{v*100:.2f}%") if div_yield else "None", ""),
    ("BETA",           safe(beta, lambda v: f"{v:.2f}"),     ""),
    ("REVENUE  (TTM)", safe(revenue, fmt_large),             "yel"),
    ("PROFIT MARGIN",  safe(margin, fmt_pct),
     "pos" if margin and margin > 0 else "neg"),
]
for col, (lbl, val, cls) in zip(cols2, row2):
    with col:
        st.markdown(f"""
        <div class="mcard">
            <div class="mlabel">{lbl}</div>
            <div class="mval {cls}" style="font-size:1.3rem;">{val}</div>
        </div>""", unsafe_allow_html=True)


#price chart
st.markdown('<div class="section-hdr">● PRICE CHART  &  VOLUME  &  MACD</div>',
            unsafe_allow_html=True)

close = hist["Close"]
hist["SMA20"]  = close.rolling(20).mean()
hist["SMA50"]  = close.rolling(50).mean()
hist["SMA200"] = close.rolling(200).mean()
bb_up, bb_mid, bb_lo = bollinger(close)
_macd, _sig, _hist_m = macd(close)

fig = make_subplots(
    rows=3, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.02,
    row_heights=[0.60, 0.18, 0.22],
)

#candles
fig.add_trace(go.Candlestick(
    x=hist.index, open=hist["Open"], high=hist["High"],
    low=hist["Low"], close=hist["Close"],
    increasing=dict(line=dict(color="#30D158", width=1), fillcolor="#30D158"),
    decreasing=dict(line=dict(color="#FF453A", width=1), fillcolor="#FF453A"),
    name="Price", showlegend=False,
), row=1, col=1)

#bollinger bands
fig.add_trace(go.Scatter(x=hist.index, y=bb_up,  line=dict(color="rgba(252,204,10,0.25)", width=1),
                          name="BB Upper", showlegend=False), row=1, col=1)
fig.add_trace(go.Scatter(x=hist.index, y=bb_lo,  line=dict(color="rgba(252,204,10,0.25)", width=1),
                          fill="tonexty", fillcolor="rgba(252,204,10,0.04)",
                          name="BB Lower", showlegend=False), row=1, col=1)
fig.add_trace(go.Scatter(x=hist.index, y=bb_mid, line=dict(color="rgba(252,204,10,0.5)", width=1, dash="dot"),
                          name="BB Mid", showlegend=False), row=1, col=1)

#smas
fig.add_trace(go.Scatter(x=hist.index, y=hist["SMA20"],  line=dict(color="#0A84FF",  width=1.5), name="SMA 20"),  row=1, col=1)
fig.add_trace(go.Scatter(x=hist.index, y=hist["SMA50"],  line=dict(color="#FF9F0A",  width=1.5), name="SMA 50"),  row=1, col=1)
if len(hist) >= 200:
    fig.add_trace(go.Scatter(x=hist.index, y=hist["SMA200"], line=dict(color="#BF5AF2", width=1.5), name="SMA 200"), row=1, col=1)

#vol
vcols = ["#30D158" if c >= o else "#FF453A"
         for c, o in zip(hist["Close"], hist["Open"])]
fig.add_trace(go.Bar(x=hist.index, y=hist["Volume"], marker_color=vcols,
                      marker_opacity=0.65, name="Volume", showlegend=False), row=2, col=1)

#macd
hcols = ["#30D158" if v >= 0 else "#FF453A" for v in _hist_m]
fig.add_trace(go.Bar(x=hist.index, y=_hist_m, marker_color=hcols, marker_opacity=0.8,
                      name="MACD Hist", showlegend=False), row=3, col=1)
fig.add_trace(go.Scatter(x=hist.index, y=_macd, line=dict(color="#0A84FF",  width=1.5), name="MACD"),   row=3, col=1)
fig.add_trace(go.Scatter(x=hist.index, y=_sig,  line=dict(color="#FF9F0A",  width=1.5), name="Signal"), row=3, col=1)

_ax      = dict(showgrid=True,  gridcolor="#1A1A1A", zeroline=False,
               showline=False, tickfont=dict(color="#636366", size=10))
_ax_nogrid = dict(showgrid=False, gridcolor="#1A1A1A", zeroline=False,
                  showline=False, tickfont=dict(color="#636366", size=10))
fig.update_layout(
    height=680,
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#636366"),
    margin=dict(l=0, r=60, t=8, b=8),
    legend=dict(orientation="h", y=1.02, x=0,
                bgcolor="rgba(0,0,0,0)", font=dict(size=11, color="#8E8E93")),
    hovermode="x unified",
    hoverlabel=dict(bgcolor="#111111", font=dict(color="#FFFFFF", size=12, family="Inter")),
    xaxis_rangeslider_visible=False,
    xaxis=dict(**_ax, showspikes=True, spikecolor="#FCCC0A", spikethickness=1),
    xaxis2=dict(**_ax),
    xaxis3=dict(**_ax),
    yaxis=dict(**_ax,       side="right"),
    yaxis2=dict(**_ax_nogrid, side="right"),
    yaxis3=dict(**_ax,       side="right"),
)
st.plotly_chart(fig, use_container_width=True)


#indicators
st.markdown('<div class="section-hdr">● TECHNICAL INDICATORS</div>', unsafe_allow_html=True)

_rsi   = rsi(close)
rsi_v  = float(_rsi.iloc[-1]) if not _rsi.empty else 50.0
rs_lbl, rs_col = rsi_label(rsi_v)

tc1, tc2, tc3, tc4 = st.columns(4)

#rsi gauge
with tc1:
    fig_g = go.Figure(go.Indicator(
        mode="gauge+number",
        value=rsi_v,
        number=dict(font=dict(size=42, color=rs_col, family="Inter"), suffix=""),
        gauge=dict(
            axis=dict(range=[0,100], tickwidth=1, tickcolor="#2C2C2E",
                      tickfont=dict(color="#636366", size=9)),
            bar=dict(color=rs_col, thickness=0.28),
            bgcolor="#111111", borderwidth=0,
            steps=[
                dict(range=[0,30],  color="rgba(48,209,88,0.15)"),
                dict(range=[30,70], color="rgba(252,204,10,0.08)"),
                dict(range=[70,100],color="rgba(255,69,58,0.15)"),
            ],
        ),
        title=dict(
            text=f"RSI (14)<br><span style='font-size:0.65em;color:{rs_col};letter-spacing:3px'>{rs_lbl}</span>",
            font=dict(size=12, color="#636366", family="Inter"),
        ),
    ))
    fig_g.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        height=200, margin=dict(l=10,r=10,t=30,b=5))
    st.plotly_chart(fig_g, use_container_width=True)

#rsi history
with tc2:
    fig_rl = go.Figure()
    fig_rl.add_hline(y=70, line_dash="dash", line_color="#FF453A", opacity=0.4)
    fig_rl.add_hline(y=30, line_dash="dash", line_color="#30D158", opacity=0.4)
    fig_rl.add_hline(y=50, line_dash="dot",  line_color="#636366", opacity=0.3)
    n = min(60, len(_rsi))
    fig_rl.add_trace(go.Scatter(
        x=hist.index[-n:], y=_rsi.iloc[-n:],
        line=dict(color="#0A84FF", width=2),
        fill="tozeroy", fillcolor="rgba(10,132,255,0.08)",
    ))
    fig_rl.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=200, margin=dict(l=5,r=5,t=30,b=5),
        title=dict(text="RSI — 60 DAY", font=dict(size=10,color="#636366",family="Inter"),x=0),
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#1A1A1A", range=[0,100],
                   side="right", tickfont=dict(color="#636366",size=9)),
        showlegend=False,
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#111111",font=dict(color="#FFF",size=11,family="Inter")),
    )
    st.plotly_chart(fig_rl, use_container_width=True)

#mini macd
with tc3:
    fig_m2 = go.Figure()
    n = min(60, len(_macd))
    h_cols = ["#30D158" if v >= 0 else "#FF453A" for v in _hist_m.iloc[-n:]]
    fig_m2.add_trace(go.Bar(x=hist.index[-n:], y=_hist_m.iloc[-n:],
                             marker_color=h_cols, marker_opacity=0.75))
    fig_m2.add_trace(go.Scatter(x=hist.index[-n:], y=_macd.iloc[-n:],
                                 line=dict(color="#0A84FF", width=2)))
    fig_m2.add_trace(go.Scatter(x=hist.index[-n:], y=_sig.iloc[-n:],
                                 line=dict(color="#FF9F0A", width=2)))
    fig_m2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=200, margin=dict(l=5,r=5,t=30,b=5),
        title=dict(text="MACD  (12 · 26 · 9)", font=dict(size=10,color="#636366",family="Inter"),x=0),
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#1A1A1A", side="right",
                   tickfont=dict(color="#636366",size=9)),
        showlegend=False,
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#111111",font=dict(color="#FFF",size=11,family="Inter")),
    )
    st.plotly_chart(fig_m2, use_container_width=True)

#yr range
with tc4:
    if hi52 and lo52 and hi52 != lo52:
        pos_pct = max(0, min(100, (raw_price - lo52) / (hi52 - lo52) * 100))
    else:
        pos_pct = 50.0
    st.markdown(f"""
    <div class="mcard" style="height:186px;display:flex;flex-direction:column;justify-content:space-between;">
        <div class="mlabel">52-WEEK RANGE</div>
        <div style="margin:8px 0 4px 0;">
            <div style="position:relative;height:4px;background:#1C1C1E;border-radius:2px;margin:18px 0 12px 0;">
                <div style="position:absolute;left:{pos_pct:.1f}%;transform:translateX(-50%);top:-6px;">
                    <div style="width:16px;height:16px;background:#FCCC0A;border-radius:50%;"></div>
                </div>
                <div style="background:linear-gradient(to right,#FF453A,#30D158);
                            height:100%;border-radius:2px;width:100%;"></div>
            </div>
            <div style="display:flex;justify-content:space-between;font-size:0.7rem;margin-top:4px;">
                <span style="color:#FF453A;">L  {safe(lo52,fmt_price)}</span>
                <span style="color:#30D158;">H  {safe(hi52,fmt_price)}</span>
            </div>
        </div>
        <div>
            <div class="mlabel">POSITION IN RANGE</div>
            <div class="mval yel">{pos_pct:.0f}%</div>
        </div>
    </div>""", unsafe_allow_html=True)

#ma status
st.markdown('<div style="height:14px;"></div>', unsafe_allow_html=True)
mc1, mc2, mc3, mc4 = st.columns(4)

def ma_stat(price, ma_series):
    v = ma_series.dropna()
    if v.empty: return "N/A", "", "—"
    m = float(v.iloc[-1])
    up = price > m
    return ("ABOVE  ▲","pos",fmt_price(m)) if up else ("BELOW  ▼","neg",fmt_price(m))

s20, c20, p20 = ma_stat(raw_price, hist["SMA20"])
s50, c50, p50 = ma_stat(raw_price, hist["SMA50"])
s200,c200,p200= ma_stat(raw_price, hist["SMA200"])

last2 = hist["Close"].iloc[-2] if len(hist) > 1 else raw_price
mom_s = "BULLISH  ▲" if raw_price >= last2 else "BEARISH  ▼"
mom_c = "pos"        if raw_price >= last2 else "neg"

for col, lbl, val, cls, sub in [
    (mc1, "VS SMA 20",  s20,   c20,   p20),
    (mc2, "VS SMA 50",  s50,   c50,   p50),
    (mc3, "VS SMA 200", s200,  c200,  p200),
    (mc4, "MOMENTUM",   mom_s, mom_c, "1-day"),
]:
    with col:
        st.markdown(f"""
        <div class="mcard">
            <div class="mlabel">{lbl}</div>
            <div class="mval {cls}" style="font-size:1.1rem;">{val}</div>
            <div class="msub">{sub}</div>
        </div>""", unsafe_allow_html=True)


#the regular stuff yk
st.markdown('<div class="section-hdr">● FUNDAMENTALS  &  ANALYST COVERAGE</div>',
            unsafe_allow_html=True)

fcf     = info.get("freeCashflow")
ocf     = info.get("operatingCashflow")
gm      = info.get("grossMargins")
om      = info.get("operatingMargins")
roe     = info.get("returnOnEquity")
roa     = info.get("returnOnAssets")
cur_r   = info.get("currentRatio")
quick_r = info.get("quickRatio")
short_r = info.get("shortRatio")
shares  = info.get("sharesOutstanding")
target  = info.get("targetMeanPrice")
rec     = info.get("recommendationKey", "N/A")
peg     = info.get("pegRatio")
ev_rev  = info.get("enterpriseToRevenue")
ev_ebit = info.get("enterpriseToEbitda")

rec_colors = {
    "strong_buy":"#30D158","buy":"#30D158",
    "hold":"#FCCC0A","neutral":"#FCCC0A",
    "underperform":"#FF9F0A","sell":"#FF453A","strong_sell":"#FF453A"
}
rec_col = rec_colors.get(rec.lower() if rec != "N/A" else "hold", "#8E8E93")

if target and raw_price:
    upside = (target - raw_price) / raw_price * 100
    upside_str = f"{upside:+.1f}%"
    upside_col = "#30D158" if upside >= 0 else "#FF453A"
else:
    upside_str = "N/A"
    upside_col = "#8E8E93"

fa, fb, fc = st.columns(3)

def row(key, val, color="#FCCC0A"):
    return f"""<div class="row-item"><span class="row-key">{key}</span>
               <span class="row-val" style="color:{color};">{val}</span></div>"""

with fa:
    st.markdown('<div class="mlabel" style="margin-bottom:6px;">CASH FLOW</div>', unsafe_allow_html=True)
    st.markdown(
        row("Free Cash Flow",       safe(fcf, fmt_large)) +
        row("Operating Cash Flow",  safe(ocf, fmt_large)) +
        '<div style="margin-top:16px;" class="mlabel">MARGINS</div>' +
        row("Gross Margin",         safe(gm, fmt_pct),  "#30D158") +
        row("Operating Margin",     safe(om, fmt_pct),  "#30D158") +
        row("Profit Margin",        safe(margin, fmt_pct),
            "#30D158" if margin and margin>0 else "#FF453A"),
        unsafe_allow_html=True
    )

with fb:
    st.markdown('<div class="mlabel" style="margin-bottom:6px;">EFFICIENCY</div>', unsafe_allow_html=True)
    st.markdown(
        row("Return on Equity",  safe(roe, fmt_pct),               "#0A84FF") +
        row("Return on Assets",  safe(roa, fmt_pct),               "#0A84FF") +
        row("Current Ratio",     safe(cur_r, lambda v:f"{v:.2f}"), "#0A84FF") +
        row("Quick Ratio",       safe(quick_r,lambda v:f"{v:.2f}"),"#0A84FF") +
        '<div style="margin-top:16px;" class="mlabel">VALUATION</div>' +
        row("PEG Ratio",         safe(peg,   lambda v:f"{v:.2f}")) +
        row("EV / Revenue",      safe(ev_rev, lambda v:f"{v:.2f}×")) +
        row("EV / EBITDA",       safe(ev_ebit,lambda v:f"{v:.2f}×")),
        unsafe_allow_html=True
    )

with fc:
    st.markdown('<div class="mlabel" style="margin-bottom:6px;">ANALYST COVERAGE</div>', unsafe_allow_html=True)
    st.markdown(
        row("Price Target",      safe(target, fmt_price))  +
        f'<div class="row-item"><span class="row-key">Upside / Downside</span>'
        f'<span class="row-val" style="color:{upside_col};">{upside_str}</span></div>' +
        f'<div class="row-item"><span class="row-key">Recommendation</span>'
        f'<span class="row-val" style="color:{rec_col};">'
        f'{rec.upper().replace("_"," ") if rec != "N/A" else "N/A"}'
        f'</span></div>' +
        row("Short Ratio",       safe(short_r, lambda v:f"{v:.1f}×"),  "#FF9F0A") +
        row("Shares Outstanding",
            safe(shares, lambda v: fmt_large(v).replace("$","")) if shares else "N/A",
            "#636366") +
        row("Debt / Equity",     safe(debt_eq, lambda v:f"{v:.0f}%"),  "#636366"),
        unsafe_allow_html=True
    )


#volume analysis
st.markdown('<div class="section-hdr">● VOLUME  ANALYSIS</div>', unsafe_allow_html=True)

avg_vol = info.get("averageVolume") or info.get("averageVolume10days")
raw_vol = info.get("regularMarketVolume") or info.get("volume") or \
          (int(hist["Volume"].iloc[-1]) if not hist["Volume"].empty else None)
vol_ratio = (raw_vol / avg_vol) if (raw_vol and avg_vol and avg_vol > 0) else None

vc1, vc2, vc3, vc4 = st.columns(4)
vol_items = [
    (vc1, "TODAY'S VOLUME",  safe(raw_vol, lambda v: f"{v:,.0f}"),  ""),
    (vc2, "AVG VOLUME",      safe(avg_vol, lambda v: f"{v:,.0f}"),  ""),
    (vc3, "VOL / AVG RATIO", safe(vol_ratio, lambda v: f"{v:.2f}×"),
     "pos" if vol_ratio and vol_ratio > 1.5 else
     "neg" if vol_ratio and vol_ratio < 0.5 else ""),
    (vc4, "DOLLAR VOLUME",
     safe(raw_vol, lambda v: fmt_large(v * raw_price)) if raw_vol else "N/A", "yel"),
]
for col, lbl, val, cls in vol_items:
    with col:
        st.markdown(f"""
        <div class="mcard">
            <div class="mlabel">{lbl}</div>
            <div class="mval {cls}" style="font-size:1.2rem;">{val}</div>
        </div>""", unsafe_allow_html=True)


#sigma news
st.markdown('<div class="section-hdr">● LATEST NEWS</div>', unsafe_allow_html=True)

news = get_news(symbol)
if news:
    for i, item in enumerate(news):
        st.markdown(f"""
        <a href="{item['link']}" target="_blank" style="text-decoration:none;display:block;">
            <div class="news-card">
                <div style="display:flex;align-items:flex-start;gap:12px;">
                    <div class="news-num">{i+1}</div>
                    <div style="flex:1;">
                        <div class="news-title">{item['title']}</div>
                        <div class="news-meta">{item['date']}</div>
                        {'<div class="news-summary">'+item["summary"]+'</div>' if item.get("summary") else ""}
                    </div>
                    <div style="color:#2C2C2E;font-size:0.9rem;flex-shrink:0;">→</div>
                </div>
            </div>
        </a>""", unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="mcard" style="text-align:center;color:#636366;padding:24px;">
        News feed unavailable — check Yahoo Finance directly.
    </div>""", unsafe_allow_html=True)


#footer
st.markdown(f"""
<div style="border-top:1px solid #1C1C1E;margin-top:48px;padding:18px 0 8px 0;
            display:flex;justify-content:space-between;align-items:center;
            color:#3A3A3C;font-size:0.6rem;letter-spacing:2px;">
    <span>STOCKLINE &nbsp;·&nbsp; DATA VIA YAHOO FINANCE</span>
    <div style="background:#FCCC0A;color:#000;font-weight:900;font-size:0.6rem;
                padding:3px 10px;letter-spacing:2px;">{symbol}</div>
    <span>UPDATED &nbsp;{datetime.now().strftime('%H:%M:%S')} UTC</span>
</div>
""", unsafe_allow_html=True)