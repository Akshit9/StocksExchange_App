import pandas as pd
import base64
import yfinance as yf
import streamlit as st
import matplotlib.pyplot as plt

st.title('Stocks Exchange App')

st.markdown("""
This app retrieves the list of Major stock exchange groups (the current top 25 by market capitalization).
* **Data Source:** [Wikipedia](http://www.wikipedia.org/wiki/List_of_S%26P_500_companies).
""")

st.sidebar.header('User Input Features')

# Web scraping of Major Stocks exchange
@st.cache
def load_data():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    html = pd.read_html(url, header = 0)
    data = html[0]
    return data

data = load_data()
sector = data.groupby('GICS Sector')

# Sidebar - Sector selection
sorted_sector_unique = sorted(data['GICS Sector'].unique())
selected_sector = st.sidebar.multiselect('Sector', sorted_sector_unique, sorted_sector_unique)

# Filtering data
data_selected_sector = data[(data['GICS Sector'].isin(selected_sector))]


st.header('Display Companies in Selected Sector')
st.write('Data Dimension: '+str(data_selected_sector.shape[0]) + ' rows and ' + str(data_selected_sector.shape[1]) + ' columns.')
st.dataframe(data_selected_sector)

# Download stocks data into a csvfile
def filedownload(data):
    csv = data.to_csv(index=False)
    bs64 = base64.b64encode(csv.encode()).decode() #strings --> bytes conversions
    href = f'<a href="data:file/csv;base64,{bs64}" download="Stocksexchange.csv"> Download CSV File</a>'
    return href

st.markdown(filedownload(data_selected_sector), unsafe_allow_html=True)

# Using yfinance
new_data = yf.download(
    tickers=list(data_selected_sector[:30].Symbol),
    period='ytd',
    interval='1d',
    group_by='ticker',
    auto_adjust=True,
    prepost=True
)

# Plotting the closing price of companies
def price_plot(Symbol):
    df = pd.DataFrame(new_data[Symbol].Close)
    df['Date'] = df.index
    plt.plot(df.Date, df.Close, color='skyblue', alpha=0.8)
    plt.xticks(rotation = 90)
    plt.title(Symbol, fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('Close')
    st.set_option('deprecation.showPyplotGlobalUse', False)
    return st.pyplot()

# Slider to select num of companies
num_company = st.sidebar.slider('Number of Companies', 1, 10)

if st.button('Show Plots'):
    st.header('Stock Closing Price')
    for i in list(data_selected_sector.Symbol)[:num_company]:
        price_plot(i)