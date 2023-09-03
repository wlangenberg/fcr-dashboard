import pandas as pd
import streamlit as st
import numpy as np
import os


st.set_page_config(
    page_title="Price Dashboard",
    page_icon=":battery:",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def getData():
    try: 
        return pd.read_csv('./data/fcr_price_data.csv', index_col=0, dtype={'Price_sek': np.float32, 'Price_eur': np.float32})
    except Exception as e:
        st.write('Working directory:', os.getcwd())
        st.error('Could not get file due to error:', e)

data = getData()


# Convert the date column to a datetime object
data['Date'] = pd.to_datetime(data.index)

st.sidebar.title('Filter')
genre = st.sidebar.radio("Välj vilken valutakurs som ska användas",
    ["SEK", "EUR"],
    captions = ["Svenska Kronor", "Euro"])

if genre == 'EUR':
    data['Price'] = data['Price_eur']
else:
    data['Price'] = data['Price_sek']

# Extract year and hour columns
data['Year'] = data['Date'].dt.year
data['Hour'] = data['Date'].dt.hour
data['Month'] = data['Date'].dt.month
month_name = ['Januari', 'Februari', 'Mars', 'April', 'Maj', 'Juni', 'Juli', 'Augusti', 'September', 'Oktober', 'November', 'December']
# Set up the Streamlit app
st.title('Dashboard: FCR Priser')

# Short introduction
st.write('')

# Sidebar for user inputs
start_date = st.sidebar.date_input('Start', data['Date'].min())
end_date = st.sidebar.date_input('Slut', data['Date'].max())

# Filter the data based on user input
filtered_data = data[(data['Date'] >= pd.Timestamp(start_date)) & (data['Date'] <= pd.Timestamp(end_date))]

# Daily average graph
st.subheader(f'Dagligt genomsnittligt pris [{genre}]')
daily_avg = filtered_data.resample('D', on='Date').mean()
st.line_chart(daily_avg['Price'])

# Monthly average graph
st.subheader(f'Genomsnittligt månadspris [{genre}]')
monthly_avg = filtered_data.copy()
monthly_avg = monthly_avg.loc[:, ['Year', 'Month', 'Price']].groupby(['Year', 'Month']).mean().reset_index()
monthly_pivot = monthly_avg.pivot(index='Month', columns='Year', values='Price')
monthly_pivot = monthly_pivot.rename(index=lambda x: f"{str(x).zfill(2)} {month_name[x-1]}")

st.line_chart(monthly_pivot)




# Yearly average graph
st.subheader(f'Genomsnittligt pris årsvis [{genre}]')
yearly_avg = filtered_data.resample('Y', on='Date').mean()
st.bar_chart(yearly_avg['Price'])

# Hourly average graph
st.subheader(f'Genomsnittligt timpris per år [{genre}]')
hourly_avg = filtered_data.groupby(['Year', 'Hour']).mean().reset_index()
hourly_pivot = hourly_avg.pivot(index='Hour', columns='Year', values='Price')
st.line_chart(hourly_pivot)

# Additional examples
# You can add more graphs and visualizations here based on your data
# For instance, you could show price distribution, correlation with other factors, etc.

# Data description
st.sidebar.markdown('**Data Beskrivning:**')
st.sidebar.write(f"Antal datapunkter: {len(data)}")

# About section
st.sidebar.markdown('**Information:**')
st.sidebar.write(f"Denna dashboard visar data för FCR priser över tidsperioden {data['Date'].min()} till {data['Date'].max()}")

# Run the Streamlit app
if __name__ == '__main__':
    st.sidebar.markdown('---')
    st.sidebar.write("FCR prisdata hämtad från: https://mimer.svk.se/")
    st.sidebar.write("Valuta data hämtad från: https://se.investing.com/currencies/eur-sek-historical-data")