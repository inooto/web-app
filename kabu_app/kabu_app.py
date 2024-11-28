import pandas as pd
import yfinance as yf
import altair as alt
import streamlit as st

st.title('株価可視化アプリ')

st.sidebar.write("""
# GAFA株価
こちらは株価可視化ツールです。以下のオプションから表示日数を指定してください。
""")

st.sidebar.write("""
## 表示日数選択
""")

days = st.sidebar.radio(label='日数',
                 options=('5days', '1month', '3months', '6months'),
                 index=0,
                 horizontal=True)

if days == '5days':
   days = '5d'
   day_w = '5'
elif days == '1month':
   days = '1mo'
   day_w = '30'
elif days == '3months':
   days = '3mo'
   day_w = '90'
else:
   days = '6mo'
   day_w = '180'

st.write(f"""
### 過去 **{day_w}日間** のGAFA株価
""")

@st.cache_data #キャッシュを使うことで表示速度速くする
def get_data(days, tickers):
  df = pd.DataFrame()
  for company in tickers.keys():
    tkr = yf.Ticker(tickers[company])
    hist = tkr.history(period=days)
    hist = hist[['Close']]
    hist.columns = [company]
    hist = hist.T
    hist.index.name = 'Name'
    df = pd.concat([df,hist])
  return df

try:
    st.sidebar.write("""
    ## 株価の指定範囲
    """)

    ymin, ymax = st.sidebar.slider(
    '範囲を指定してください',
    0.0,3500.0, (0.0, 3500.0)
    )

    tickers = {
        'apple': 'AAPL',
        'facebook': 'META',
        'google': 'GOOGL',
        'microsoft': 'MSFT',
        'netflix': 'NFLX',
        'amazon': 'AMZN'
    }

    df = get_data(days, tickers)

    companies = st.multiselect(
    '会社名を選択してください.',
    list(df.index),
    ['google','amazon','facebook','apple']
    )

    if not companies:
        st.error('少なくとも一社は選んでください.')

    else:
        data = get_data(days, tickers).loc[companies]
        st.write('###  株価 (USD)',data.sort_index())

        data = data.T.reset_index()
        data = pd.melt(data, id_vars=['Date']).rename( #meltはpipot関数の逆を行っている
            columns={'value': 'Stock Prices(USD)'}
        )

        chart = (
            alt.Chart(data)
            .mark_line(opacity=0.8, clip=True)
            .encode(
                x="Date:T",
                y=alt.Y("Stock Prices(USD):Q", stack=None,scale=alt.Scale(domain=[ymin,ymax])),
                color='Name:N'
            )
        )

        st.altair_chart(chart, use_container_width=True)

except:
   st.error(
      "エラーが発生しています."
   )
