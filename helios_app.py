import streamlit as st
import pandas as pd
import plotly.express as px

# Load the Excel file
excel_file = "Pointage Helios.xlsx"

# Read the sheet RECAP FRT with correct header and skip rows
df = pd.read_excel(excel_file, sheet_name="RECAP FRT", skiprows=2, usecols="E:G", engine="openpyxl")
df.columns = ["RANG", "DATE DEBUT", "DATE FIN"]

# Drop rows with missing RANG or dates
df = df.dropna(subset=["RANG", "DATE DEBUT", "DATE FIN"])

# Convert dates to datetime
df["DATE DEBUT"] = pd.to_datetime(df["DATE DEBUT"])
df["DATE FIN"] = pd.to_datetime(df["DATE FIN"])

# Streamlit app layout
st.set_page_config(page_title="Suivi des Travaux - Hélios", layout="wide")
st.title("📊 Suivi de l'Avancement des Travaux - Hélios")

# Filter by RANG
unique_rangs = sorted(df["RANG"].unique())
selected_rangs = st.multiselect("Sélectionner les phases (RANG) à afficher :", unique_rangs, default=unique_rangs)

filtered_df = df[df["RANG"].isin(selected_rangs)]

# Create Gantt chart
fig = px.timeline(
    filtered_df,
    x_start="DATE DEBUT",
    x_end="DATE FIN",
    y="RANG",
    color="RANG",
    title="Diagramme de Gantt des Phases de Production",
)

fig.update_yaxes(categoryorder="total ascending")
fig.update_layout(height=600, xaxis_title="Date", yaxis_title="Phase (RANG)")

st.plotly_chart(fig, use_container_width=True)

# Show data table
with st.expander("📋 Voir les données brutes"):
    st.dataframe(filtered_df)
