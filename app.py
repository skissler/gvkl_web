import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(layout="wide")
st.title("Viral Kinetics Explorer")

DEFAULT_PATH = os.path.join("data", "combined_cleaned_data.csv")

uploaded_file = st.file_uploader("Upload your viral kinetics CSV (or use default below)", type=["csv"])

# Load data
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("Using uploaded file.")
else:
    df = pd.read_csv(DEFAULT_PATH)
    st.info("Using default viral kinetics dataset.")

# Clean data
df["Log10VL"] = pd.to_numeric(df["Log10VL"], errors="coerce")
df_clean = df.dropna(subset=["Log10VL", "TimeDays", "PersonID"])

# --- Sidebar filters ---
st.sidebar.header("Filters")

# Determine overall min/max of all reported age ranges
min_age = int(df_clean["AgeRng1"].min())
max_age = int(df_clean["AgeRng2"].max())

# Slider for selecting age window
selected_age_range = st.sidebar.slider(
    "Age Range (include if age group intersects this range)",
    min_value=min_age,
    max_value=max_age,
    value=(min_age, max_age)
)

# Other filters
study_options = df_clean["StudyID"].dropna().unique()
sample_options = df_clean["SampleType"].dropna().unique()
selected_studies = st.sidebar.multiselect("Study ID", options=study_options, default=list(study_options))
selected_samples = st.sidebar.multiselect("Sample Type", options=sample_options, default=list(sample_options))

# Apply filters
df_filtered = df_clean[
    (df_clean["AgeRng2"] >= selected_age_range[0]) &
    (df_clean["AgeRng1"] <= selected_age_range[1]) &
    (df_clean["StudyID"].isin(selected_studies)) &
    (df_clean["SampleType"].isin(selected_samples))
]

# Preview filtered data
st.markdown("### Filtered Data Preview")
st.write(df_filtered.head())

# Plot viral load over time
sample_ids = df_filtered["PersonID"].unique()[:10]  # Limit to 10 people
df_sample = df_filtered[df_filtered["PersonID"].isin(sample_ids)]

fig, ax = plt.subplots(figsize=(10, 6))
for pid, group in df_sample.groupby("PersonID"):
    ax.plot(group["TimeDays"], group["Log10VL"], label=f"Person {pid}", alpha=0.6)

ax.set_title("Viral Load Over Time (Sample of 10 People)")
ax.set_xlabel("Days Since Symptom Onset or Exposure")
ax.set_ylabel("Log10 Viral Load")
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')
ax.grid(True)
st.pyplot(fig)
