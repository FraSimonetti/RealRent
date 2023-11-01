import pandas as pd
import plotly.express as px
import streamlit as st 
from itertools import chain
# PANDAS DATABASE CREATION
st.set_page_config(
  page_title="Sales Dashboard",
  page_icon=":bar_chart:",
  layout="wide"                 
)
@st.cache_data 

def get_data_from_excel():
    df = pd.read_excel('TEST.xlsx').
    # Add 'hour' column to dataframe for second barchart
    return df

df=get_data_from_excel()

# Convert the column to a numeric data type
df['Prezzo richiesto €'] = pd.to_numeric(df['Prezzo richiesto €'])
df['Tasso Medio Giornaliero (TMG) €'] = pd.to_numeric(df['Tasso Medio Giornaliero (TMG) €'])
df['Stanze'] = pd.to_numeric(df['Stanze'])

def map_stanze_to_description(Stanze):
    if Stanze == 1:
        return "Monolocale"
    elif Stanze == 2:
        return "Bilocale"
    elif Stanze == 3:
        return "Trilocale"
    elif Stanze == 4:
        return "Quadrilocale"
    elif Stanze > 4:
        return "Più di 4 stanze"
    else:
        return "N/A"

# Create the new "Numero di Stanze" column based on the mapping
df['Numero_Stanze'] = df['Stanze'].apply(map_stanze_to_description)


#st.dataframe(df) 

# SIDEBAR

# MAINPAGE
st.title(":bar_chart: RealRent Summary Dashboard")
st.markdown("##")

st.sidebar.header("Please Filter Here:")

all_areas = ["View All"] + df["Zona"].unique().tolist()
all_room_types = ["View All"] + df["Numero_Stanze"].unique().tolist()

zona = st.sidebar.selectbox("Select the area:", all_areas)
numero_Stanze = st.sidebar.selectbox("Select the number of room:", all_room_types)

# Handle "View All" option
if zona == "View All" and numero_Stanze == "View All":
    df_selection = df  # Show all data
else:
    if zona == "View All":
        zona = df["Zona"].unique()
    else:
        zona = [zona]

    if numero_Stanze == "View All":
        numero_Stanze = df["Numero_Stanze"].unique()
    else:
        numero_Stanze = [numero_Stanze]

    df_selection = df[(df["Zona"].isin(zona)) & (df["Numero_Stanze"].isin(numero_Stanze))]

st.dataframe(df_selection)



# TOP KPI's
average_sales_price =round(df_selection["Prezzo richiesto €"].mean(),1)
#average_number_room =round(df_selection["Stanze"].mean(),1)
average_price_night_bnb =round(df_selection["Tasso Medio Giornaliero (TMG) €"].mean(),1)


# KPI's COLUMNS
left_column,middle_column,right_column=st.columns(3)


with left_column:
  st.subheader("Prezzo medio di vendita:")
  st.subheader(f"€ {average_sales_price:,}") 
kpi_column = st.columns(3)
with middle_column:
     st.subheader("Numero di immobili trovati:")
     st.subheader(f"{len(df_selection):,}")
with right_column:
  st.subheader("Prezzo medio per notte (BnB):")
  st.subheader(f"€ {average_price_night_bnb:,}")


st.markdown("---")

# BARCHARTS

# PRICE BY ZONA [BAR CHART]

Price_by_room=(df_selection.groupby(by=["Zona"]).mean()[["Prezzo richiesto €"]].sort_values(by="Prezzo richiesto €"))
Price_by_room = Price_by_room.dropna()
fig_product_sales = px.bar(
    Price_by_room,
    x="Prezzo richiesto €",
    y=Price_by_room.index,
    orientation="h",
    title="<b>Prezzo medio di vendita per zona</b>",
    color_discrete_sequence=["#205295"] * len(Price_by_room),
    template="plotly_white",
)

fig_product_sales.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)

# PREZZO PER NOTTE BY ZONA [BAR CHART]

sales_by_hour=df_selection.groupby(by=["Zona"]).mean()[["Tasso Medio Giornaliero (TMG) €"]].sort_values(by="Tasso Medio Giornaliero (TMG) €")
sales_by_hour = sales_by_hour.dropna()
fig_hourly_sales=px.bar(
    sales_by_hour,
    x=sales_by_hour.index,
    y="Tasso Medio Giornaliero (TMG) €",
    title="<b>Prezzo medio per notte per zona</b>",
    color_discrete_sequence=["#205295"] * len(sales_by_hour),
    template="plotly_white",
)

fig_hourly_sales.update_layout(
    xaxis=dict(tickmode="linear"),
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False)),
)

# PREZZO PER NOTTE by numero di stanza [BAR CHART]

sales_by_room=df_selection.groupby(by=["Numero_Stanze"]).mean()[["Tasso Medio Giornaliero (TMG) €"]].sort_values(by="Tasso Medio Giornaliero (TMG) €")
sales_by_room = sales_by_room.dropna()
fig_third_graph=px.bar(
    sales_by_room,
    x=sales_by_room.index,
    y="Tasso Medio Giornaliero (TMG) €",
    title="<b>Prezzo medio di vendita per tipologia di appartamento</b>",
    color_discrete_sequence=["#205295"] * len(sales_by_room),
    template="plotly_white",
)

fig_third_graph.update_layout(
    xaxis=dict(tickmode="linear"),
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False)),
)

# Displaying charts

left_column, middle_column, right_column = st.columns(3)
left_column.plotly_chart(fig_product_sales, use_container_width=True)
middle_column.plotly_chart(fig_hourly_sales, use_container_width=True)
right_column.plotly_chart(fig_third_graph, use_container_width=True)

# HIDE STREAMLIT STYLE
hide_st_style="""
            <style>
            #MainMenu {visibility:hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """

st.markdown(hide_st_style, unsafe_allow_html=True)


