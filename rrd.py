import pandas as pd
import plotly.graph_objs as go
import streamlit as st
import numpy as np
import seaborn as sns
import altair as alt



# Set the page configuration at the beginning of your script



# Page setup:
st.set_page_config(
    page_title="RealRent Dashboard",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
    'About': 'https://real-rent.it/',
    'Get help': "https://real-rent.it/contact"
    }
)
st.markdown("Questa dashboard ha esclusivamente uno scopo illustrativo e dimostrativo. I dati visualizzati qui sono generici e non rappresentano alcuna situazione reale. Per ulteriori informazioni o per richiedere l'accesso alla nostra dashboard ufficiale, vi invitiamo a scriverci all'indirizzo e-mail realrent.tech@gmail.com o contattarci direttamente cliccando sul pulante qui sotto!")
st.link_button("Contattaci", "https://real-rent.it/contact")
@st.cache_data
def get_data_from_excel():
    try:
        df = pd.read_excel('TEST.xlsx')
        return df
    except FileNotFoundError:
        st.error("Excel file not found.")
        st.stop()
    except Exception as e:
        st.error(f"An error occurred while reading the Excel file: {str(e)}")
        st.stop()

df = get_data_from_excel()

# Convert the column to a numeric data type
df['Prezzo richiesto €'] = pd.to_numeric(df['Prezzo richiesto €'], errors='coerce')
df['Tasso Medio Giornaliero (TMG) €'] = pd.to_numeric(df['Tasso Medio Giornaliero (TMG) €'], errors='coerce')
df['Stanze'] = pd.to_numeric(df['Stanze'], errors='coerce')

# Define the mapping function
def map_stanze_to_description(stanze):
    if stanze == 1:
        return "Monolocale"
    elif stanze == 2:
        return "Bilocale"
    elif stanze == 3:
        return "Trilocale"
    elif stanze == 4:
        return "Quadrilocale"
    elif stanze > 4:
        return "Più di 4 stanze"
    else:
        return "N/A"

# Create the new "Numero di Stanze" column based on the mapping
df['Numero_Stanze'] = df['Stanze'].apply(map_stanze_to_description)

# SIDEBAR

# MAIN PAGE
st.title(":bar_chart: RealRent Summary Dashboard")
st.markdown("##")
st.sidebar.header("Please Filter Here:")

all_areas = ["View All"] + df["Zona"].unique().tolist()
all_room_types = ["View All"] + df["Numero_Stanze"].unique().tolist()

zona = st.sidebar.multiselect("Select the area:", all_areas, default="View All")
numero_stanze = st.sidebar.multiselect("Select the number of rooms:", all_room_types, default="View All")

# Handle "View All" option
if "View All" in zona and "View All" in numero_stanze:
    df_selection = df  # Show all data
else:
    zona = zona if "View All" not in zona else df["Zona"].unique()
    numero_stanze = numero_stanze if "View All" not in numero_stanze else df["Numero_Stanze"].unique()
    df_selection = df.query('Zona in @zona and Numero_Stanze in @numero_stanze')
    
st.dataframe(df_selection)

st.markdown("---")

# TOP KPI's
average_sales_price = round(df_selection["Prezzo richiesto €"].mean(), 1)
average_price_night_bnb = round(df_selection["Tasso Medio Giornaliero (TMG) €"].mean(), 1)

# KPI's COLUMNS
left_column, middle_column, right_column = st.columns(3)

with left_column:
    st.subheader("Prezzo medio di vendita:")
    st.subheader(f"€ {average_sales_price:,.2f}")
with middle_column:
    st.subheader("Numero di immobili trovati:")
    st.subheader(f"{len(df_selection):,}")
with right_column:
    st.subheader("Prezzo medio per notte (BnB):")
    st.subheader(f"€ {average_price_night_bnb:,.2f}")

st.markdown("---")

# BAR CHARTS
average_prices = df_selection.groupby("Zona")["Prezzo richiesto €"].mean().round(1)
average_prices = average_prices.sort_values(ascending=False)

# Create a bar chart for average prices
fig_product_sales = go.Figure(data=[go.Bar(
    x=average_prices.index,
    y=average_prices,
    marker=dict(line=dict(color='white', width=2)),
)])

fig_product_sales.update_layout(
    title_text="<b>Prezzo medio di vendita per zona<b>",
    title_font_size=24,
    xaxis_title="Quartiere",
    yaxis_title="Prezzo medio di vendita",
)

# Calculate average prices for BnB
average_prices_bnb = df_selection.groupby("Zona")["Tasso Medio Giornaliero (TMG) €"].mean().round(1)

# Sort the data by average prices in descending order
average_prices_bnb = average_prices_bnb.sort_values(ascending=False)

# Create a bar chart for BnB average prices
fig_hourly_sales = go.Figure(data=[go.Bar(
    x=average_prices_bnb.index,
    y=average_prices_bnb,
    marker=dict(line=dict(color='white', width=2)),
)])

fig_hourly_sales.update_layout(
    title_text="<b>Prezzo medio per singola notte (BnB) </b>",
    title_font_size=24,
    xaxis_title="Quartiere",
    yaxis_title="Prezzo medio per notte",
)
# Splitting the charts into two columns:
left, right = st.columns(2)

# Columns (content):
with left:
    st.plotly_chart(fig_product_sales, use_container_width=True)
with right:
    st.plotly_chart(fig_hourly_sales, use_container_width=True)
    
st.markdown('---')

with st.container():
   st.write("Seleziona un quartiere per evidenziarne i singoli immobili e confrontarli rispetto a quelli degli altri quartieri")
# Widgets:
# Filter data based on city selection:
# Widgets:
cities = sorted(list(df['Zona'].unique()))
city_selection = st.selectbox('🌎 Seleziona un quartiere', cities)

# City selection:
your_city = city_selection
selected_city = df.query('Zona == @your_city')
other_cities = df.query('Zona != @your_city')


# Create a scatter plot for Prezzo richiesto € and Tasso Medio Giornaliero (TMG) €
# Create a scatter plot for Prezzo richiesto € and Tasso Medio Giornaliero (TMG) €
scatter_plot = alt.Chart(df).mark_circle(size=100).encode(
    x=alt.X('Prezzo richiesto €', title='Prezzo richiesto €'),
    y=alt.Y('Tasso Medio Giornaliero (TMG) €', title='Prezzo medio per notte €'),
    color=alt.condition(
        alt.datum.Zona == city_selection,
        alt.value('#00FF7F'),
        alt.value('lightgrey')
    ),
 tooltip=[
        alt.Tooltip('Zona:N', title='Zona'),
        alt.Tooltip('Prezzo richiesto €:Q', title='Prezzo richiesto €', format='.2s'),
        alt.Tooltip('Tasso Medio Giornaliero (TMG) €:Q', title='Prezzo medio per notte', format='.1f')
    ]
).properties(width=600, height=400).configure_axis(grid=False)

# Showing up the numerical df (as a dfframe):
# Center the dataframe using columns
# Create three columns to center the dataframe
left,right = st.columns([1, 1])

sorted_df = df.query('Zona == @your_city')[['Zona', 'Prezzo richiesto €', 'Tasso Medio Giornaliero (TMG) €', 'Stanze', 'Rendimento (Autogestito) %', 'Rendimento (Dato in gestione) %', 'Link Immobiliare.it']]
sorted_df = sorted_df.sort_values(by='Rendimento (Autogestito) %', ascending=False)

sorted_df.reset_index(drop=True, inplace=True)

# Show the scatter
left, right = st.columns(2)

with left:
    st.altair_chart(scatter_plot, use_container_width=True)
    st.markdown('<br>', unsafe_allow_html=True)  # Use HTML for space

# Show the DataFrame without the index column
with right:
    st.dataframe(sorted_df, use_container_width=True)
