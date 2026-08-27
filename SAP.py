import pandas as pd
import numpy as np
import streamlit as st
import re
st.title("NTPC SAP Notifications Analysis")
uploaded_file = st.file_uploader("Upload your defect data (Excel/CSV)", type=["xlsx", "csv"])
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".xlsx"):
            data = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith(".csv"):
            data = pd.read_csv(uploaded_file)
        else:
            st.error("Unsupported file format.")
            st.stop()
        st.success("File loaded successfully!")

        # Date conversion
        data["Notif.date"] = pd.to_datetime(data["Notif.date"], format="%Y%m%d", errors="coerce")
        data["Functional Loc."] = data["Functional Loc."].astype(str)
        data["equipment"] = data["equipment"].astype(str)
        data["Description"] = data["Description"].astype(str)

        st.subheader("Total SAP notifications considered for analysis")
        st.subheader(data1.shape[0])

        # Top repeated equipment
        st.subheader("Top 20 Repeated equipment notifications")
        temp = data[data["equipment"] != "KORBA STATION COMMON"].copy()
        repeat_defects = temp.groupby("equipment").size().reset_index(name="Count")
        repeated = repeat_defects[repeat_defects["Count"] > 50].sort_values(["Count", "equipment"], ascending=[False, True]).head(20)
        st.dataframe(repeated)

        # System-wise analysis
        COL = "Functional Loc."
        EQUIP = "equipment"

        def is_valid_parent(s):
            hyphens = s.count("-")
            if hyphens < 2 or hyphens > 3:
                return False
            parts = s.split("-")
            return not re.search(r"\d", parts[2] if len(parts) >= 3 else "")

        def extract_parent(s):
            parts = s.split("-")
            return "-".join(parts[:3]) if len(parts) >= 3 else s

        data1["parent"] = data1[COL].apply(extract_parent)
        df_valid = data1[data1["parent"].apply(is_valid_parent)].copy()
        df_unique = df_valid.drop_duplicates("parent")[["parent", EQUIP]]
        appearance = data1.groupby("parent").size().reset_index(name="Total Count")
        df_final = df_unique.merge(appearance, on="parent", how="left")
        df_final = df_final[df_final["Total Count"] > 40].sort_values("Total Count", ascending=False).reset_index(drop=True)

        total_appearances = df_final["Total Count"].sum()
        df_final["%"] = ((df_final["Total Count"] / total_appearances) * 100).round().astype(int) if total_appearances > 0 else 0
        df_final.rename(columns={"parent": COL}, inplace=True)

        st.subheader("System wise no. of defects in last 10 years")
        st.dataframe(df_final)

        # Stage-wise summary
        stages = {"Stage-1": "S1COM", "Stage-2": "S2COM", "Stage-3": "S3COM"}
        stage_summary = []

        for stage, keyword in stages.items():
            count = data["Functional Loc."].str.contains(keyword, na=False).sum()
            stage_summary.append({"Stage": stage, "Total Defects": count})

        stage_df = pd.DataFrame(stage_summary)
        grand_total = stage_df["Total Defects"].sum()
        stage_df["% Contribution"] = ((stage_df["Total Defects"] / grand_total) * 100).round(0) if grand_total > 0 else 0

        st.subheader("📊 All Stage-wise Defect Summary")
        st.dataframe(stage_df)

        fig, ax = plt.subplots(figsize=(7, 7))
        ax.pie(stage_df["Total Defects"], labels=stage_df["Stage"], autopct="%1.1f%%", startangle=90)
        ax.set_title("Stage-wise Defect Distribution")
        ax.axis("equal")
        st.pyplot(fig)

        # Defect categories
        defect_patterns = {
            "Gland Leak Related": r"gland|galand|GLD",
            "Vibrational Related": r"vibration|vib",
            "Bearing/Coupling Abnormalities": r"sound|bearing|brng|thrust",
            "NRV Passing": r"nrv",
            "Valve Issues": r"valve|vlv|v/v|bfv",
            "Oil Leakage": r"oil",
            "Reverse Rotation/Decoupled": r"reverse|decouple",
            "Pipe Leakages": r"pipe|line|hdr|header",
            "Overloading/Tripping": r"overload|OL|O/L|current|curren",
            "Pump Pressure Issues": r"pr low|develop|pressure|devlp",
            "Choking Issues": r"choke",
            "Jamming Issues": r"jam"
        }

        summary = []

        for defect_name, pattern in defect_patterns.items():
            count = data["Description"].str.contains(pattern, case=False, na=False).sum()
            percent = round((count / len(data)) * 100, 2) if len(data) > 0 else 0
            summary.append({"Defect Category": defect_name, "Count": count, "% of Total": percent})

        summary_df = pd.DataFrame(summary).sort_values("Count", ascending=False).reset_index(drop=True)

        st.subheader("📊 Defect Summary")
        st.dataframe(summary_df)

        # Stage selection
        st.subheader("Select the stage for detailed Analysis:")
        selected = st.multiselect("Select:", list(stages.keys()))

        if selected:
            for stage in selected:
                data2 = data[data["Functional Loc."].str.contains(stages[stage], na=False)].copy()

                st.subheader(f"{stage} - Total defects")
                st.write(data2.shape[0])

                # Top 10 repeated equipment
                repeat_defects = data2.groupby("equipment").size().reset_index(name="Count")
                repeated = repeat_defects[repeat_defects["Count"] > 10].sort_values(["Count", "equipment"], ascending=[False, True]).head(10).copy()
                repeated["Each notification interval in terms of weeks"] = (520 / repeated["Count"]).round().astype(int)

                st.subheader("TOP 10 repeated defects in the selected stage")
                st.dataframe(repeated)

                # Detailed defect categories
                detailed_patterns = {
                    "Gland Leak": r"gland|galand|GLD",
                    "Vibrational Issues": r"vibration|vib",
                    "Bearing/Coupling Issues": r"sound|bearing|brng|thrust",
                    "NRV Passing": r"nrv",
                    "Valve Issues": r"valve|vlv|v/v|bfv",
                    "Oil Leak/Oil Top-up": r"oil",
                    "Reverse/Decoupled": r"reverse|decouple",
                    "Pipe Leakage": r"pipe|line|hdr|header",
                    "Overloading/Tripping": r"overload|OL|O/L|current|curren",
                    "Pump Pressure": r"pr low|develop|pressure|devlp",
                    "Line/CT Nozzle Choking": r"choke",
                    "Valve/Pump/Gearbox Jamming": r"jam"
                }

                category_counts = {}

                for name, pattern in detailed_patterns.items():
                    temp = data2[data2["Description"].str.contains(pattern, case=False, na=False)].copy()
                    temp["Year"] = temp["Notif.date"].dt.year
                    category_counts[name] = len(temp)

                    st.subheader(f"📅 Year-wise {name}")

                    yearly_count = temp.groupby("Year").size().reset_index(name="Count")
                    st.bar_chart(yearly_count, x="Year", y="Count")

                    st.write(f"No. of {name}: {len(temp)}")

                # Category coverage
                total_categories = sum(category_counts.values())
                percentage = int((total_categories / len(data2)) * 100) if len(data2) > 0 else 0
                st.write("% of notifications divided into various categories:", percentage, "%")

                # Equipment-wise defects
                equip_count = data2["equipment"].value_counts().reset_index()
                equip_count.columns = ["equipment", "Defect_Count"]

                st.subheader("⚙️ Equipment-wise defect count in selected stage")
                st.dataframe(equip_count)

                # Forecast selection
                selected_equips = st.multiselect(
                    f"Select equipment(s) to forecast for {stage}:",
                    equip_count["equipment"].tolist(),
                    key=f"equipment_{stage}"
                )

                forecast_results = []

                for eq in selected_equips:
                    eq_dates = data2.loc[data2["equipment"] == eq, "Notif.date"].dropna().sort_values()

                    if len(eq_dates) > 1:
                        gaps = eq_dates.diff().dt.days.dropna()
                        avg_gap = gaps.mean()
                        last_date = eq_dates.max()
                        next_pred_date = last_date + pd.Timedelta(days=avg_gap)

                        forecast_results.append({
                            "Equipment": eq,
                            "Total Defects": len(eq_dates),
                            "Average Gap (days)": round(avg_gap, 1),
                            "Last Defect Date": last_date.date(),
                            "Predicted Next Defect": next_pred_date.date()
                        })

                if forecast_results:
                    result = pd.DataFrame(forecast_results)
                    st.subheader("📅 Forecasted Next Defect Dates")
                    st.dataframe(result)

    except Exception as e:
        st.error(f"Error while processing the file: {e}")
