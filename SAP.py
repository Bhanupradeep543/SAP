import io
import random
import base64
from datetime import datetime

import pandas as pd
import numpy as np
import streamlit as st

st.set_page_config(layout="wide")
st.title("NTPC SAP Notifications Analysis")

# -------------------------
# Helper functions
# -------------------------
def read_uploaded_file(uploaded_file):
    """Read uploaded file (xls/xlsx/csv) into a DataFrame."""
    name = uploaded_file.name.lower()
    try:
        if name.endswith(".csv"):
            return pd.read_csv(uploaded_file)
        elif name.endswith(".xls") or name.endswith(".xlsx"):
            return pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file type. Please upload .csv, .xls or .xlsx")
            return None
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None

def safe_contains(series, pattern, flags=0):
    """Wrapper for str.contains with na=False to avoid errors on NaN."""
    return series.astype(str).str.contains(pattern, flags=flags, na=False)

def show_yearly_bar(yearly_count_df, year_col, value_col, title):
    """Show a bar chart using Year as index (safe for Streamlit)."""
    if yearly_count_df.empty:
        st.write("No data to display for:", title)
        return
    display = yearly_count_df.set_index(year_col)[value_col]
    st.subheader(title)
    st.bar_chart(display)

# -------------------------
# Upload and basic checks
# -------------------------
uploaded_file = st.file_uploader("Upload your defect data (Excel/CSV)", type=["xlsx", "xls", "csv"])
if uploaded_file is None:
    st.info("Please upload an Excel or CSV file to continue.")
    st.stop()  # stop further execution until file uploaded

data = read_uploaded_file(uploaded_file)
if data is None or data.empty:
    st.error("No data loaded from the uploaded file.")
    st.stop()

st.success("File loaded successfully")

# -------------------------
# Ensure expected columns exist
# -------------------------
required_cols = ["Notif.date", "Main WorkCtr", "equipment", "Functional Loc.", "Description"]
missing = [c for c in required_cols if c not in data.columns]
if missing:
    st.error(f"The uploaded file is missing required columns: {missing}")
    st.stop()

# -------------------------
# Date parsing (safe)
# -------------------------
# Attempt to parse in multiple likely formats; coerce errors to NaT
data = data.copy()
data.loc[:, "Notif.date"] = pd.to_datetime(data["Notif.date"], errors="coerce", infer_datetime_format=True)
if data["Notif.date"].isna().all():
    st.warning("All values in 'Notif.date' could not be parsed. Check date format.")
# Keep working even if some dates are NaT

# -------------------------
# Basic KPI & filtering
# -------------------------
data1 = data[data["Main WorkCtr"] == "M400CWCT"].copy()
st.subheader("Total SAP notifications considered for analysis (Main WorkCtr = M400CWCT)")
st.subheader(data1.shape[0])

# Exclude common equipment
data_filtered = data[~(data["equipment"].astype(str) == "KORBA STATION COMMON")].copy()

st.subheader("Top 20 Repeated equipment notifications (excluding KORBA STATION COMMON)")
repeat_defects = data_filtered.groupby(["equipment"]).size().reset_index(name="Count")
repeated = repeat_defects[repeat_defects["Count"] > 50]
repeated = repeated.sort_values(by=["Count", "equipment"], ascending=[False, True]).head(20)
st.write(repeated)

# -------------------------
# Keywords mapping and counting
# -------------------------
KEYWORDS = [
    "1017-S1COM-ACW-ACL","1017-S1COM-ACW-ACT","1017-S1COM-CLT-T01","1017-S1COM-CLT-T02","1017-S1COM-CLT-T03","1017-S1COM-CTS",
    "1017-S1COM-CWS","1017-S1COM-CWS-SWP","1017-S1COM-CWS-TWS","1017-S2COM-CLT-T4A","1017-S2COM-CLT-T4B","1017-S2COM-CLT-T5A","1017-S2COM-CLT-T5B",
    "1017-S2COM-CLT-T6A","1017-S2COM-CLT-T6B","1017-S2COM-CTS","1017-S2COM-CWS-CHL","1017-S2COM-CWS","1017-S2COM-CWS-SWP","1017-S2COM-CWS-TS",
    "1017-S3COM-CLT-T7A","1017-S3COM-CLT-T7B","1017-S3COM-CWS"
]
KEYWORD_MAP = {
    "1017-S1COM-ACW-ACL":"ADD.CLARIFIED PUMP SYSTEM","1017-S1COM-ACW-ACT":"ADD.CLARIFIED COOLING TOWERS","1017-S1COM-CLT-T01":"ST-1 COOLING TOWER-1",
    "1017-S1COM-CLT-T02":"ST-1 COOLING TOWER-2","1017-S1COM-CLT-T03":"ST-1 COOLING TOWER-3","1017-S1COM-CTS":"ST-1 CT PUMPS SYSTEM","1017-S1COM-CWS":"ST-1 CW SYSTEM",
    "1017-S1COM-CWS-SWP":"ST-1 SCREEN WASH PUMPS SYSTEM","1017-S1COM-CWS-TWS":"ST-1 TWS SYSTEM","1017-S2COM-CLT-T4A":"ST-2 COOLING TOWER 4A",
    "1017-S2COM-CLT-T4B":"ST-2 COOLING TOWER 4B","1017-S2COM-CLT-T5A":"ST-2 COOLING TOWER 5A","1017-S2COM-CLT-T5B":"ST-2 COOLING TOWER 5B",
    "1017-S2COM-CLT-T6A":"ST-2 COOLING TOWER 6A","1017-S2COM-CLT-T6B":"ST-2 COOLING TOWER 6B","1017-S2COM-CTS":"ST-2 CT PUMPS SYSTEM",
    "1017-S2COM-CWS-CHL":"ST-2 CW CHLORINATION SYSTEM","1017-S2COM-CWS":"ST-2 CW SYSTEM","1017-S2COM-CWS-SWP":"ST-2 SCREEN WASH PUMP SYSTEM",
    "1017-S2COM-CWS-TS":"ST-2 TWS SYSTEM","1017-S3COM-CLT-T7A":"ST-3 COOLING TOWER 7A","1017-S3COM-CLT-T7B":"ST-3 COOLING TOWER 7B","1017-S3COM-CWS":"ST-3 CW SYSTEM"
}
COLUMN_NAME = "Functional Loc."

if COLUMN_NAME not in data.columns:
    st.error(f"Column '{COLUMN_NAME}' not found in data.")
else:
    col_data = data[COLUMN_NAME].astype(str)
    results = []
    for kw in KEYWORDS:
        # count occurrences (exact substring search)
        count = col_data.str.contains(kw, na=False).sum()
        final_name = KEYWORD_MAP.get(kw, kw)
        results.append({"Keyword": final_name, "Count": int(count)})
    result_df = pd.DataFrame(results)
    total = result_df["Count"].sum()
    if total == 0:
        result_df["Percentage"] = 0
    else:
        result_df["Percentage"] = (result_df["Count"] / total * 100).astype(int)
    result_df = result_df.sort_values(by="Count", ascending=False).reset_index(drop=True)
    st.write("System wise number of defects (based on Functional Loc.)")
    st.dataframe(result_df)

# -------------------------
# Stage selection & analysis
# -------------------------
keywords = {"Stage-1": "S1COM", "Stage-2": "S2COM", "Stage-3": "S3COM"}
selected = st.multiselect("Select the stage:", list(keywords.keys()))
if selected:
    selected_keywords = [keywords[s] for s in selected]
else:
    selected_keywords = []

# We'll prepare equip_count default so it's available later even if no stage selected
equip_count = pd.DataFrame(columns=["equipment", "Defect_Count"])

forecast_results = []

for k in selected_keywords:
    # filter for selected stage and ensure safe copy
    data2 = data[data["Functional Loc."].astype(str).str.contains(k, na=False)].copy()

    st.subheader(f"Stage filter: {k} — Total defects")
    st.write(data2.shape[0])

    # top repeated defects in selected stage
    repeat_defects = data2.groupby(["equipment"]).size().reset_index(name="Count")
    repeated = repeat_defects[repeat_defects["Count"] > 10].copy()
    repeated = repeated.sort_values(by=["Count", "equipment"], ascending=[False, True]).head(10)
    st.subheader("TOP 10 repeated defects in the selected stage")
    df = repeated.copy()
    multiplier = 520
    if not df.empty:
        df.loc[:, "each notification interval in terms of weeks"] = ((multiplier) / df["Count"]).round().astype(int)
    st.write(df)

    # --- Various issue categories (use regex-like OR but case-insensitive)
    # Gland leaks
    data3 = data2[data2["Description"].astype(str).str.contains("gland", na=False)].copy()
    data3.loc[:, "Year"] = data3["Notif.date"].dt.year
    st.write("no.of gland leaks in the selected stage", data3.shape[0])
    yearly_count = data3.groupby("Year")["Notif.date"].count().reset_index()
    yearly_count.rename(columns={"Notif.date": "gland leak"}, inplace=True)
    show_yearly_bar(yearly_count, "Year", "gland leak", "📅 Year-wise gland leaks")

    # Vibration
    data4 = data2[data2["Description"].astype(str).str.contains("vib", na=False)].copy()
    data4.loc[:, "Year"] = data4["Notif.date"].dt.year
    st.write("no.of vibrational issues in the selected stage", data4.shape[0])
    yearly_count = data4.groupby("Year")["Notif.date"].count().reset_index()
    yearly_count.rename(columns={"Notif.date": "vibrational issues"}, inplace=True)
    show_yearly_bar(yearly_count, "Year", "vibrational issues", "📅 Year-wise vibrational issues")

    # Bearing/coupling/sound
    data5 = data2[data2["Description"].astype(str).str.contains("sound|bearing|brng|thrust", na=False)].copy()
    data5.loc[:, "Year"] = data5["Notif.date"].dt.year
    st.write("no.of bearing/coupling issues in the selected stage", data5.shape[0])
    yearly_count = data5.groupby("Year")["Notif.date"].count().reset_index()
    yearly_count.rename(columns={"Notif.date": "bearing/coupling issues"}, inplace=True)
    show_yearly_bar(yearly_count, "Year", "bearing/coupling issues", "📅 Year-wise bearing/coupling issues")

    # NRV passing
    data6 = data2[data2["Description"].astype(str).str.contains("nrv", na=False)].copy()
    data6.loc[:, "Year"] = data6["Notif.date"].dt.year
    st.write("no.of NRV passing issues in the selected stage", data6.shape[0])
    yearly_count = data6.groupby("Year")["Notif.date"].count().reset_index()
    yearly_count.rename(columns={"Notif.date": "NRV passing"}, inplace=True)
    show_yearly_bar(yearly_count, "Year", "NRV passing", "📅 Year-wise NRV passings")

    # Valve issues
    data7 = data2[data2["Description"].astype(str).str.contains("valve|vlv|bfv|v/v", na=False)].copy()
    data7.loc[:, "Year"] = data7["Notif.date"].dt.year
    st.write("no.of valve issues in the selected stage", data7.shape[0])
    yearly_count = data7.groupby("Year")["Notif.date"].count().reset_index()
    yearly_count.rename(columns={"Notif.date": "Valve issues"}, inplace=True)
    show_yearly_bar(yearly_count, "Year", "Valve issues", "📅 Year-wise Valve issues")

    # Oil issues
    data8 = data2[data2["Description"].astype(str).str.contains("oil", na=False)].copy()
    data8.loc[:, "Year"] = data8["Notif.date"].dt.year
    st.write("no.of oil leak/ oil top up issues in the selected stage", data8.shape[0])
    yearly_count = data8.groupby("Year")["Notif.date"].count().reset_index()
    yearly_count.rename(columns={"Notif.date": "Oil leaks/ oil top up issues"}, inplace=True)
    show_yearly_bar(yearly_count, "Year", "Oil leaks/ oil top up issues", "📅 Year-wise Oil leaks/ oil top up issues")

    # Decouple/reverse
    data9 = data2[data2["Description"].astype(str).str.contains("reverse|decouple", na=False)].copy()
    data9.loc[:, "Year"] = data9["Notif.date"].dt.year
    st.write("no.of pump/Fan shaft Decoupled/reverse rotational issues in the selected stage", data9.shape[0])
    yearly_count = data9.groupby("Year")["Notif.date"].count().reset_index()
    yearly_count.rename(columns={"Notif.date": "pump/Fan shaft jam/reverse rotational issues"}, inplace=True)
    show_yearly_bar(yearly_count, "Year", "pump/Fan shaft jam/reverse rotational issues", "📅 Year-wise pump/Fan shaft Decouple/reverse issues")

    # Pipe leakage (note: fixed bug earlier referencing data9 wrongly)
    data10 = data2[data2["Description"].astype(str).str.contains("pipe|line", na=False)].copy()
    data10.loc[:, "Year"] = data10["Notif.date"].dt.year
    st.write("no.of Pipe leakage issues in the selected stage", data10.shape[0])
    yearly_count = data10.groupby("Year")["Notif.date"].count().reset_index()
    yearly_count.rename(columns={"Notif.date": "Pipe leakage issues"}, inplace=True)
    show_yearly_bar(yearly_count, "Year", "Pipe leakage issues", "📅 Year-wise Pipe leakage issues")

    # Overload/tripping
    data11 = data2[data2["Description"].astype(str).str.contains("overload|o/l|current", na=False)].copy()
    data11.loc[:, "Year"] = data11["Notif.date"].dt.year
    st.write("no.of Over loading/ tripping issues in the selected stage", data11.shape[0])
    yearly_count = data11.groupby("Year")["Notif.date"].count().reset_index()
    yearly_count.rename(columns={"Notif.date": "Over loading/ tripping issues"}, inplace=True)
    show_yearly_bar(yearly_count, "Year", "Over loading/ tripping issues", "📅 Year-wise Over loading/ tripping issues")

    # -------------------------
    # Equipment frequency and forecasting prep (per stage)
    # -------------------------
    date_col = "Notif.date"
    equip_col = "equipment"

    # Convert date_col to datetime safely (it's already parsed above, but ensure local copy)
    data2 = data2.copy()
    data2.loc[:, date_col] = pd.to_datetime(data2[date_col], errors="coerce")
    data2 = data2.dropna(subset=[date_col, equip_col])
    data2.loc[:, equip_col] = data2[equip_col].astype(str)

    equip_count = data2[equip_col].value_counts().reset_index()
    equip_count.columns = [equip_col, "Defect_Count"]
    st.subheader("⚙️ Equipment-wise defect frequency (for selected stage)")
    st.dataframe(equip_count)

    # Forecast logic (append per equipment)
    for eq in equip_count[equip_count["Defect_Count"] > 0][equip_col].tolist():
        eq_data = data2[data2[equip_col] == eq].sort_values(by=date_col).copy()
        eq_dates = eq_data[date_col].dropna().sort_values()
        if len(eq_dates) > 1:
            gaps = eq_dates.diff().dt.days.dropna()
            if not gaps.empty:
                avg_gap = gaps.mean()
                last_date = eq_dates.max()
                next_pred_date = last_date + pd.Timedelta(days=avg_gap)
                forecast_results.append({
                    "Equipment": eq,
                    "Total_Defects": int(len(eq_dates)),
                    "Average_Gap_(days)": round(float(avg_gap), 1),
                    "Last_Defect_Date": last_date.date(),
                    "Predicted_Next_Defect": next_pred_date.date()
                })

# -------------------------
# Final forecast results (aggregate across selected stages)
# -------------------------
if forecast_results:
    result_df = pd.DataFrame(forecast_results)
    st.subheader("📅 Forecasted Next Defect Dates")
    st.dataframe(result_df)
else:
    st.info("No forecast results to show (select a stage and ensure equipments have at least 2 dated events).")
