# To deploy locally, run this in bash: 
# streamlit run app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from scipy.optimize import curve_fit
import numpy as np
from utils.plotting import save_streamlit_style_figure
from utils.modeling import piecewise_linear, fit_piecewise

st.set_page_config(layout="wide")

# -- for styling -- 
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <style>
    html, body, div, span, h1, h2, h3, h4, h5, h6, p, label, input, textarea {
        font-family: 'Montserrat', sans-serif !important;
    }
    </style>
""", unsafe_allow_html=True)

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
# st.write(df_filtered.head(100))
st.write(df_filtered)

# Plot viral load over time
sample_ids = df_filtered["PersonID"].unique()[:25]  # Limit to 25 people
df_sample = df_filtered[df_filtered["PersonID"].isin(sample_ids)]

# Determine which grouping columns exist and have non-null values
grouping_cols = ["PersonID"]
if "InfectionID" in df_sample.columns and df_sample["InfectionID"].notna().any():
    grouping_cols.append("InfectionID")
if "SampleType" in df_sample.columns and df_sample["SampleType"].notna().any():
    grouping_cols.append("SampleType")

fig, ax = plt.subplots(figsize=(10, 6))

# Plot each trajectory
for _, group in df_sample.groupby(grouping_cols):
    # Apply GE/ml transformation if slope and intercept are present
    if {"GEml_conversion_slope", "GEml_conversion_intercept"}.issubset(group.columns):
        ge_values = group["Log10VL"] * group["GEml_conversion_slope"] + group["GEml_conversion_intercept"]
    else:
        ge_values = group["Log10VL"]  # fallback to raw if conversion values missing

    ax.plot(
        group["TimeDays"], ge_values,
        color='black',
        alpha=0.2,
        linewidth=1,
        marker='o',
        markersize=4,
        markerfacecolor='black',
        markeredgewidth=0,
    )

ax.set_title("Viral Load Over Time (Sample of 25 People)")
ax.set_xlabel("Time (days)")

# Update y-axis label based on transformation
if {"GEml_conversion_slope", "GEml_conversion_intercept"}.issubset(df_sample.columns):
    ax.set_ylabel("Log10 Genome Equivalents per ml (GE/ml, transformed)")
else:
    ax.set_ylabel("Log10 Viral Load")

ax.grid(True)
ax.set_facecolor("white")

# Display in Streamlit
st.pyplot(fig)


# -- Fit to a single person -- 
# person_ids = df_filtered["PersonID"].unique()
# selected_person = st.selectbox("Select a person to fit model to", options=person_ids)
# df_person = df_filtered[df_filtered["PersonID"] == selected_person].sort_values("TimeDays")

# fit_params = fit_piecewise(df_person)

# st.markdown("### Piecewise Linear Fit")

# fig2, ax2 = plt.subplots(figsize=(8, 5))
# ax2.scatter(df_person["TimeDays"], df_person["Log10VL"], label="Observed", color="blue")

# if fit_params is not None:
#     t_fit = np.linspace(df_person["TimeDays"].min(), df_person["TimeDays"].max(), 200)
#     y_fit = piecewise_linear(t_fit, *fit_params)
#     ax2.plot(t_fit, y_fit, label="Piecewise Fit", color="red", linewidth=2)
#     ax2.set_title("Piecewise Linear Fit to Viral Kinetics")
#     ax2.set_xlabel("Time (days)")
#     ax2.set_ylabel("Log10 Viral Load")
#     ax2.legend()
# else:
#     ax2.set_title("Fit failed for this individual.")

# st.pyplot(fig2)

