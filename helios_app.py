import streamlit as st
import pandas as pd
import plotly.express as px

# Load the Excel file and the sheet 'BD Hélios'
excel_file = 'Pointage Helios.xlsx'
sheet_name = 'BD Hélios'
df = pd.read_excel(excel_file, sheet_name=sheet_name, engine='openpyxl')

# Convert DATE_POINT to datetime
df['DATE_POINT'] = pd.to_datetime(df['DATE_POINT'], errors='coerce')

# Drop rows with missing RANG or DATE_POINT
df = df.dropna(subset=['RANG', 'DATE_POINT'])

# Group by RANG and get min and max DATE_POINT
gantt_data = df.groupby('RANG').agg(
    start_date=('DATE_POINT', 'min'),
    end_date=('DATE_POINT', 'max'),
    libelle=('LIBELLE', 'first')
).reset_index()

# Streamlit UI
st.set_page_config(page_title="Suivi Helios", layout="wide")
st.title("📊 Diagramme de Gantt – Suivi des Phases (BD Hélios)")

# Filter by RANG
selected_rangs = st.multiselect("Sélectionner les phases (RANG)", options=gantt_data['RANG'].unique(), default=gantt_data['RANG'].unique())
filtered_data = gantt_data[gantt_data['RANG'].isin(selected_rangs)]

# Create Gantt chart
fig = px.timeline(
    filtered_data,
    x_start="start_date",
    x_end="end_date",
    y="RANG",
    color="libelle",
    title="Avancement des phases par RANG",
    labels={"libelle": "Tâche"}
)
fig.update_yaxes(categoryorder="total ascending")

# Display chart
st.plotly_chart(fig, use_container_width=True)
