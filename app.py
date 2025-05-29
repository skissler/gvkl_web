import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from scipy.optimize import curve_fit
import numpy as np

def piecewise_linear(t, t1, t2, t3, y0, s1, s2):
    """
    Piecewise linear viral kinetics:
    y = y0 (baseline)
      + s1 * (t - t1) if t1 < t < t2 (rise)
      + s2 * (t - t2) if t2 < t < t3 (fall)
      + 0 otherwise
    All lines are connected.
    """
    y = np.full_like(t, y0)
    y += np.where(t >= t1, s1 * (np.minimum(t, t2) - t1), 0)
    y += np.where(t >= t2, s2 * (np.minimum(t, t3) - t2), 0)
    return y


def fit_piecewise(df_person):
    t = df_person["TimeDays"].values
    y = df_person["Log10VL"].values

    # Reasonable initial guesses
    t1_init = np.percentile(t, 10)
    t2_init = np.percentile(t, 40)
    t3_init = np.percentile(t, 80)
    y0_init = np.min(y)
    s1_init = 1.0
    s2_init = -1.0

    p0 = [t1_init, t2_init, t3_init, y0_init, s1_init, s2_init]

    try:
        popt, _ = curve_fit(piecewise_linear, t, y, p0=p0)
        return popt
    except RuntimeError:
        return None

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
st.write(df_filtered.head(11))

# Plot viral load over time
sample_ids = df_filtered["PersonID"].unique()[:25]  # Limit to 25 people
df_sample = df_filtered[df_filtered["PersonID"].isin(sample_ids)]

fig, ax = plt.subplots(figsize=(10, 6))
for pid, group in df_sample.groupby("PersonID"):
    ax.plot(group["TimeDays"], group["Log10VL"], label=f"Person {pid}", alpha=0.6)

ax.set_title("Viral Load Over Time (Sample of 25 People)")
ax.set_xlabel("Days Since Symptom Onset or Exposure")
ax.set_ylabel("Log10 Viral Load")
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')
ax.grid(True)
# fig.savefig("plot.png", dpi=300)
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

