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
st.title('Vad är FCR?')
st.write("""
        FCR-N (Frequency Containment Reserve – Normal), eller Frekvenshållningsreserv normaldrift på svenska, är en term som används inom ramen för balanstjänster för elnät.
        Frekvenshållningsreserver (FCR) har till uppgift att stabilisera frekvensen vid frekvensavvikelser och är grundläggande för att kunna hålla balansen. 
        De aktiveras automatiskt om frekvensen ändras inom det frekvensområde de ska stötta. FCR handlas upp i förväg för varje ögonblick under dygnet.
        Det finns flera olika FCR-produkter. FCR-N är den frekvenshållningsreserv som används vid normal drift.     
         """)

st.write("""
        Priset EUR/MW, eller Pris per megawatt på svenska, 
        i sammanhanget med FCR-N, 
        hänvisar till kostnaden per megawatt (MW) av reservkraft som tillhandahålls eller köps för att upprätthålla frekvenskontroll. 
        Detta pris används vanligtvis för att fastställa den ekonomiska ersättningen för leverantörer av FCR-N-tjänster eller de avgifter som uppstår när nätföretag köper dessa tjänster.
         """)

st.title('Dashboard för FCR Priser över tid')

# Short introduction
st.write('Denna dashboard är skapad för att enkelt kunna visualisera de historiska priserna för FCR-N på den svenska och danska marknaden.')

st.write('Datat avser medelpris uppmätt i SEK/MW (eller EUR/MW) för avropad kapacitet av FCR-N, baserat på svenska och danska BA (ej TSO-handel). Datum och tid anges i CET/CEST.')

st.write('Prisdatat är hämtat från mimer som svenska kraftnät ansvarar för. Datat är från början uttryckt i EUR, vilket vi omvandlat till SEK genom att använda historiskt data för växelkursen EUR/SEK.')


# Sidebar for user inputs
start_date = st.sidebar.date_input('Start', data['Date'].min(), data['Date'].min(), data['Date'].max())
end_date = st.sidebar.date_input('Slut', data['Date'].max(), data['Date'].min(), data['Date'].max())

# Filter the data based on user input
filtered_data = data[(data['Date'] >= pd.Timestamp(start_date)) & (data['Date'] <= pd.Timestamp(end_date))]
data_count = len(filtered_data)
max_date = max(filtered_data['Date'])
min_date = min(filtered_data['Date'])


# Daily average graph
st.subheader(f'Dagligt genomsnittligt pris [{genre}]')
daily_avg = filtered_data.resample('D', on='Date').mean()
st.line_chart(daily_avg['Price'])

st.write('Grafen avser medelvärde för priset varje dag.')

# Monthly average graph
st.subheader(f'Genomsnittligt månadspris [{genre}]')
monthly_avg = filtered_data.copy()
monthly_avg = monthly_avg.loc[:, ['Year', 'Month', 'Price']].groupby(['Year', 'Month']).mean().reset_index()
monthly_pivot = monthly_avg.pivot(index='Month', columns='Year', values='Price')
monthly_pivot = monthly_pivot.rename(index=lambda x: f"{str(x).zfill(2)} {month_name[x-1]}")
st.line_chart(monthly_pivot)

st.write("Grafen visar ett medelvärde för varje månad, där varje år urskiljs med en separat linje. Detta för att enklare jämföra månatliga förändringar mellan olika år.")


# Yearly average graph
st.subheader(f'Genomsnittligt pris årsvis [{genre}]')
yearly_avg = filtered_data.resample('Y', on='Date').mean()
st.bar_chart(yearly_avg['Price'])


# Hourly average graph
st.subheader(f'Genomsnittligt timpris per år [{genre}]')
hourly_avg = filtered_data.groupby(['Year', 'Hour']).mean().reset_index()
hourly_pivot = hourly_avg.pivot(index='Hour', columns='Year', values='Price')
st.line_chart(hourly_pivot)

st.write("Grafen visar ett medelvärde för varje timme på dygnet, där varje år visas på en separat linje.")

# Additional examples
# You can add more graphs and visualizations here based on your data
# For instance, you could show price distribution, correlation with other factors, etc.

# Data description
st.sidebar.markdown('---')
st.sidebar.markdown('**Beskrivning av data:**')
st.sidebar.write(f"* Antal datapunkter: {data_count}")
st.sidebar.write(f"* Graferna i dashboarden avnänder data över tidsperioden {str(min_date).split(' ')[0]} till {str(max_date).split(' ')[0]}")
st.sidebar.markdown('---')
st.sidebar.write("FCR prisdata hämtad från: https://mimer.svk.se/")
st.sidebar.write("Växelkurser hämtad från: https://se.investing.com/currencies/eur-sek-historical-data")