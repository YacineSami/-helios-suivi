import streamlit as st
import pandas as pd
import plotly.express as px

# Charger les données
file_path = "Pointage Helios.xlsx"

# Lecture de la feuille BD Hélios
df = pd.read_excel(file_path, sheet_name="BD Hélios", engine="openpyxl")

# Nettoyage des colonnes
df["RANG"] = pd.to_numeric(df["RANG"], errors="coerce").astype("Int64")
df["NB_HEURES"] = pd.to_numeric(df["NB_HEURES"], errors="coerce")
df["DATE_POINT"] = pd.to_datetime(df["DATE_POINT"], errors="coerce")

# Lecture de la feuille RECAP FRT
recap = pd.read_excel(file_path, sheet_name="RECAP FRT", engine="openpyxl", skiprows=2)
recap_clean = recap.iloc[:, [4, 5, 6, 8]]
recap_clean.columns = ["RANG", "DATE_DEBUT", "DATE_FIN", "OBJECTIF"]
recap_clean = recap_clean.dropna(subset=["RANG"])
recap_clean["RANG"] = pd.to_numeric(recap_clean["RANG"], errors="coerce").astype("Int64")
recap_clean["DATE_DEBUT"] = pd.to_datetime(recap_clean["DATE_DEBUT"], errors="coerce")
recap_clean["DATE_FIN"] = pd.to_datetime(recap_clean["DATE_FIN"], errors="coerce")
recap_clean["OBJECTIF"] = pd.to_numeric(recap_clean["OBJECTIF"], errors="coerce")

# Fusion des données
merged = df.merge(recap_clean, on="RANG", how="left")

# Calcul du temps total passé par phase
phase_summary = merged.groupby("RANG").agg({
    "NB_HEURES": "sum",
    "DATE_POINT": ["min", "max"],
    "LIBELLE": "first",
    "DATE_DEBUT": "first",
    "DATE_FIN": "first",
    "OBJECTIF": "first"
}).reset_index()

phase_summary.columns = ["RANG", "HEURES_TOTALES", "DATE_DEBUT_REELLE", "DATE_FIN_REELLE", "LIBELLE", "DATE_DEBUT_PLAN", "DATE_FIN_PLAN", "OBJECTIF"]

# Détection des alertes
def detect_alerts(row):
    alerts = []
    if pd.notnull(row["OBJECTIF"]) and row["HEURES_TOTALES"] < row["OBJECTIF"]:
        alerts.append("✅ En avance")
    elif pd.notnull(row["OBJECTIF"]) and row["HEURES_TOTALES"] > row["OBJECTIF"]:
        alerts.append("⚠️ En retard")
    elif pd.notnull(row["OBJECTIF"]) and row["HEURES_TOTALES"] == row["OBJECTIF"]:
        alerts.append("✔️ Terminé à temps")
    return ", ".join(alerts)

phase_summary["ALERTE"] = phase_summary.apply(detect_alerts, axis=1)

# Interface Streamlit
st.set_page_config(page_title="Suivi Helios", layout="wide")
st.title("📊 Suivi d'Avancement des Travaux - Helios")

# Diagramme de Gantt
st.subheader("Diagramme de Gantt par Phase")
gantt_data = phase_summary.dropna(subset=["DATE_DEBUT_REELLE", "DATE_FIN_REELLE"])
fig = px.timeline(
    gantt_data,
    x_start="DATE_DEBUT_REELLE",
    x_end="DATE_FIN_REELLE",
    y="LIBELLE",
    color="ALERTE",
    title="Avancement des Phases",
    labels={"LIBELLE": "Phase"}
)
fig.update_yaxes(autorange="reversed")
st.plotly_chart(fig, use_container_width=True)

# Tableau de suivi
st.subheader("Tableau de Suivi des Phases")
st.dataframe(phase_summary[["RANG", "LIBELLE", "HEURES_TOTALES", "OBJECTIF", "ALERTE"]])

# Alertes spécifiques
st.subheader("🔔 Alertes")
for _, row in phase_summary.iterrows():
    if row["ALERTE"]:
        st.markdown(f"- **Phase {row['RANG']} ({row['LIBELLE']})** : {row['ALERTE']}")
