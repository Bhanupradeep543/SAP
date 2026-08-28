import pandas as pd
import numpy as np
import streamlit as st
import io
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

st.set_page_config(page_title="NTPC SAP Analysis", layout="wide")
st.title("🏭 NTPC SAP Notifications Analysis")

patterns = {"Gland Leak":r"gland|galand|GLD","Vibration":r"vibration|vib","Bearing/Coupling":r"sound|bearing|brng|thrust","NRV Passing":r"nrv","Valve Issues":r"valve|vlv|v/v|bfv","Oil Leakage":r"oil","Reverse/Decoupled":r"reverse|decouple","Pipe Leakage":r"pipe|line|hdr|header","Overloading/Tripping":r"overload|OL|O/L|current|curren","Pump Pressure":r"pr low|develop|pressure|devlp","Choking":r"choke","Jamming":r"jam"}

def defect_summary(df):
    result = [{"Defect Category":name,"Count":int(df["Description"].str.contains(pattern,case=False,na=False,regex=True).sum())} for name,pattern in patterns.items()]
    return pd.DataFrame(result).sort_values("Count",ascending=False).reset_index(drop=True)

def yearly_category_data(df,pattern):
    temp = df[df["Description"].str.contains(pattern,case=False,na=False,regex=True)].copy()
    years = sorted(df["Notif.date"].dropna().dt.year.unique())
    return temp.groupby(temp["Notif.date"].dt.year).size().reindex(years,fill_value=0).reset_index(name="Count")

def style_table(table):
    table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#404040")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("ALIGN",(0,0),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("GRID",(0,0),(-1,-1),0.5,colors.black),("FONTSIZE",(0,0),(-1,-1),8),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F2F2F2")])]))

def pdf_report(plant_df,plant,forecasts=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer,pagesize=landscape(A4),rightMargin=25,leftMargin=25,topMargin=25,bottomMargin=25)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleStyle",parent=styles["Title"],alignment=TA_CENTER,fontSize=20,spaceAfter=15)
    heading_style = ParagraphStyle("HeadingStyle",parent=styles["Heading2"],fontSize=14,spaceBefore=10,spaceAfter=8)
    normal_style = ParagraphStyle("NormalStyle",parent=styles["BodyText"],fontSize=9,leading=13)
    elements = []

    elements.append(Paragraph("NTPC SAP Notifications Analysis Report",title_style))
    elements.append(Paragraph(f"<b>Selected Plant:</b> {plant}",styles["Heading2"]))
    elements.append(Paragraph(f"<b>Report Generated:</b> {pd.Timestamp.now().strftime('%d-%m-%Y %H:%M')}",normal_style))
    elements.append(Spacer(1,15))

    total_notifications = len(plant_df)
    total_equipment = plant_df["equipment"].nunique()
    first_date = plant_df["Notif.date"].min() if plant_df["Notif.date"].notna().any() else None
    last_date = plant_df["Notif.date"].max() if plant_df["Notif.date"].notna().any() else None
    years = sorted(plant_df["Notif.date"].dropna().dt.year.unique())

    elements.append(Paragraph("1. Selected Plant Summary",heading_style))
    summary = [["Parameter","Value"],["Plant",plant],["Total Notifications",total_notifications],["Total Equipment",total_equipment],["Years Covered",len(years)],["First Notification",first_date.strftime("%d-%m-%Y") if first_date is not None else "N/A"],["Last Notification",last_date.strftime("%d-%m-%Y") if last_date is not None else "N/A"]]
    table = Table(summary,colWidths=[220,220])
    style_table(table)
    elements.append(table)
    elements.append(Spacer(1,15))

    elements.append(Paragraph("2. Defect Category Summary",heading_style))
    detail = defect_summary(plant_df)
    detail["Percentage"] = np.where(total_notifications>0,(detail["Count"]/total_notifications*100).round(2),0)
    defect_table = [["Defect Category","Count","Percentage (%)"]] + detail[["Defect Category","Count","Percentage"]].values.tolist()
    table = Table(defect_table,repeatRows=1)
    style_table(table)
    elements.append(table)
    elements.append(PageBreak())

    elements.append(Paragraph("3. Year-wise Trend of All Defect Categories",heading_style))
    yearly_rows = [["Defect Category"]+[str(y) for y in years]]
    for category,pattern in patterns.items():
        temp = plant_df[plant_df["Description"].str.contains(pattern,case=False,na=False,regex=True)].copy()
        yearly_rows.append([category]+[int((temp["Notif.date"].dt.year==year).sum()) for year in years])
    table = Table(yearly_rows,repeatRows=1)
    style_table(table)
    elements.append(table)
    elements.append(PageBreak())

    elements.append(Paragraph("4. Detailed Category-wise Yearly Analysis",heading_style))
    for category,pattern in patterns.items():
        temp = plant_df[plant_df["Description"].str.contains(pattern,case=False,na=False,regex=True)].copy()
        total_category = len(temp)
        elements.append(Paragraph(f"<b>{category}</b> - Total Notifications: {total_category}",normal_style))
        if len(years)>0:
            trend = yearly_category_data(plant_df,pattern)
            trend_table = [["Year","Notifications"]]+trend.values.tolist()
            table = Table(trend_table,colWidths=[100,120],repeatRows=1)
            style_table(table)
            elements.append(table)
        else:
            elements.append(Paragraph("No valid notification dates available.",normal_style))
        elements.append(Spacer(1,10))

    elements.append(PageBreak())
    elements.append(Paragraph("5. Equipment-wise Notification Analysis",heading_style))
    eq = plant_df["equipment"].value_counts().reset_index()
    eq.columns = ["Equipment","Count"]
    eq["Interval (weeks)"] = np.where(eq["Count"]>0,(520/eq["Count"]).round().astype(int),0)
    eq = eq.head(20)
    equipment_table = [["Equipment","Count","Interval (weeks)"]]+eq.values.tolist()
    table = Table(equipment_table,repeatRows=1)
    style_table(table)
    elements.append(table)

    if forecasts:
        elements.append(Spacer(1,15))
        elements.append(Paragraph("6. Equipment Defect Forecast",heading_style))
        forecast_df = pd.DataFrame(forecasts)
        forecast_table = [forecast_df.columns.tolist()]+forecast_df.values.tolist()
        table = Table(forecast_table,repeatRows=1)
        style_table(table)
        elements.append(table)

    elements.append(PageBreak())
    elements.append(Paragraph("7. Management-Level Detailed Analysis",heading_style))

    highest = detail.iloc[0] if not detail.empty else None
    nonzero = detail[detail["Count"]>0].sort_values("Count")
    lowest = nonzero.iloc[0] if not nonzero.empty else None
    top_equipment = eq.iloc[0] if not eq.empty else None

    if highest is not None:
        elements.append(Paragraph(f"<b>Highest Defect Category:</b> {highest['Defect Category']} with {int(highest['Count'])} notifications, representing {highest['Percentage']:.2f}% of total plant notifications.",normal_style))
        elements.append(Spacer(1,8))

    if lowest is not None:
        elements.append(Paragraph(f"<b>Lowest Occurring Defect Category:</b> {lowest['Defect Category']} with {int(lowest['Count'])} notifications.",normal_style))
        elements.append(Spacer(1,8))

    if top_equipment is not None:
        elements.append(Paragraph(f"<b>Highest Notification Equipment:</b> {top_equipment['Equipment']} with {int(top_equipment['Count'])} notifications.",normal_style))
        elements.append(Spacer(1,8))

    elements.append(Paragraph("<b>Reliability Recommendation:</b> High-frequency defect categories should be prioritised for RCA, condition monitoring, preventive maintenance optimisation and spare planning. Repeated notifications should be evaluated for permanent corrective action instead of repetitive breakdown maintenance.",normal_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer

files = st.file_uploader("Upload Excel/CSV files from different plants",type=["xlsx","csv"],accept_multiple_files=True)

if files:

    st.subheader("🏭 Assign Plant Name")

    file_data = []

    for i,f in enumerate(files):
        c1,c2 = st.columns([2,1])
        with c1: st.write(f"📄 {f.name}")
        with c2: plant = st.text_input("Plant Name",key=f"plant{i}",placeholder="Korba")
        if plant: file_data.append((f,plant))

    if file_data:

        frames = []

        for f,plant in file_data:
            try:
                d = pd.read_excel(f,engine="openpyxl") if f.name.lower().endswith(".xlsx") else pd.read_csv(f)
                d["Plant"] = plant
                frames.append(d)
            except Exception as e:
                st.error(f"{f.name}: {e}")

        if frames:

            data = pd.concat(frames,ignore_index=True)

            required = ["Notif.date","equipment","Description","Functional Loc."]
            missing = [c for c in required if c not in data.columns]

            if missing:
                st.error(f"Missing columns: {missing}")
                st.stop()

            data["Notif.date"] = pd.to_datetime(data["Notif.date"],format="%Y%m%d",errors="coerce")

            for c in ["equipment","Description","Functional Loc."]:
                data[c] = data[c].astype(str)

            st.success(f"{len(data):,} notifications loaded from {data['Plant'].nunique()} plants.")

            # ============================================================
            # OVERALL DASHBOARD
            # ============================================================

            st.header("📊 Overall Dashboard")

            c1,c2,c3,c4 = st.columns(4)
            c1.metric("Total Notifications",f"{len(data):,}")
            c2.metric("Plants",data["Plant"].nunique())
            c3.metric("Equipment",data["equipment"].nunique())
            c4.metric("Years",data["Notif.date"].dt.year.nunique())

            plant_summary = data.groupby("Plant").size().reset_index(name="Notifications").sort_values("Notifications",ascending=False)

            st.subheader("🏭 Plant-wise Notifications")
            st.dataframe(plant_summary,use_container_width=True)
            st.bar_chart(plant_summary.set_index("Plant"))

            # ============================================================
            # PLANT-WISE DEFECT DASHBOARD
            # ============================================================

            dashboard = []

            for plant in data["Plant"].unique():
                d = data[data["Plant"]==plant]
                row = {"Plant":plant,"Total":len(d)}
                row.update({name:int(d["Description"].str.contains(pattern,case=False,na=False,regex=True).sum()) for name,pattern in patterns.items()})
                dashboard.append(row)

            dashboard_df = pd.DataFrame(dashboard)

            st.subheader("🔧 Plant-wise Defect Dashboard")
            st.dataframe(dashboard_df,use_container_width=True)

            overall = defect_summary(data)

            st.subheader("📈 Overall Defect Distribution")
            st.dataframe(overall,use_container_width=True)
            st.bar_chart(overall.set_index("Defect Category"))

            # ============================================================
            # PLANT SELECTION
            # ============================================================

            st.header("🔍 Detailed Plant Analysis")

            plant_options = ["-- Select Plant --"]+sorted(data["Plant"].unique())
            selected_plant = st.selectbox("Select Plant for Detailed Analysis",plant_options,index=0)

            # ============================================================
            # IMPORTANT: DETAILED ANALYSIS ONLY AFTER PLANT SELECTION
            # ============================================================

            if selected_plant != "-- Select Plant --":

                plant_df = data[data["Plant"]==selected_plant].copy()

                st.success(f"Detailed analysis displayed only for selected plant: {selected_plant}")

                # ========================================================
                # SELECTED PLANT KPI
                # ========================================================

                c1,c2,c3,c4 = st.columns(4)

                c1.metric("Notifications",len(plant_df))
                c2.metric("Equipment",plant_df["equipment"].nunique())
                c3.metric("First Notification",str(plant_df["Notif.date"].min().date()) if plant_df["Notif.date"].notna().any() else "N/A")
                c4.metric("Last Notification",str(plant_df["Notif.date"].max().date()) if plant_df["Notif.date"].notna().any() else "N/A")

                # ========================================================
                # SELECTED PLANT DEFECT SUMMARY
                # ========================================================

                st.subheader(f"📊 Defect Category Analysis - {selected_plant}")

                detail = defect_summary(plant_df)
                detail["Percentage"] = np.where(len(plant_df)>0,(detail["Count"]/len(plant_df)*100).round(2),0)

                st.dataframe(detail,use_container_width=True)

                st.bar_chart(detail.set_index("Defect Category")["Count"])

                # ========================================================
                # YEAR-WISE ALL CATEGORY TREND
                # ========================================================

                st.subheader(f"📅 Year-wise Defect Trends - {selected_plant}")

                years = sorted(plant_df["Notif.date"].dropna().dt.year.unique())

                yearly_rows = [["Defect Category"]+[str(y) for y in years]]

                for category,pattern in patterns.items():
                    temp = plant_df[plant_df["Description"].str.contains(pattern,case=False,na=False,regex=True)].copy()
                    yearly_rows.append([category]+[int((temp["Notif.date"].dt.year==year).sum()) for year in years])

                yearly_all = pd.DataFrame(yearly_rows[1:],columns=yearly_rows[0])

                st.dataframe(yearly_all,use_container_width=True)

                # ========================================================
                # INDIVIDUAL CATEGORY TRENDS
                # ========================================================

                st.subheader(f"📈 Detailed Category-wise Yearly Trends - {selected_plant}")

                for category,pattern in patterns.items():

                    temp = plant_df[plant_df["Description"].str.contains(pattern,case=False,na=False,regex=True)].copy()

                    yearly = temp.groupby(temp["Notif.date"].dt.year).size().reindex(years,fill_value=0).reset_index(name="Count")

                    st.markdown(f"### 🔹 {category}")

                    st.write(f"Total {category}: **{len(temp):,} notifications**")

                    if len(yearly)>0:
                        st.bar_chart(yearly.set_index("Notif.date")["Count"])
                    else:
                        st.info("No valid year-wise data available.")

                # ========================================================
                # EQUIPMENT ANALYSIS
                # ========================================================

                st.subheader(f"⚙️ Equipment-wise Notifications - {selected_plant}")

                eq = plant_df["equipment"].value_counts().reset_index()
                eq.columns = ["Equipment","Count"]
                eq["Interval (weeks)"] = np.where(eq["Count"]>0,(520/eq["Count"]).round().astype(int),0)

                st.dataframe(eq.head(20),use_container_width=True)

                # ========================================================
                # FORECAST
                # ========================================================

                st.subheader(f"🔮 Equipment Defect Forecast - {selected_plant}")

                selected_eq = st.multiselect("Select Equipment for Forecast",eq["Equipment"].tolist(),key=f"eq_{selected_plant}")

                forecasts = []

                for equipment in selected_eq:

                    dates = plant_df.loc[plant_df["equipment"]==equipment,"Notif.date"].dropna().sort_values()

                    if len(dates)>1:

                        gap = dates.diff().dt.days.dropna().mean()
                        last = dates.max()

                        forecasts.append({"Equipment":equipment,"Defects":len(dates),"Average Gap (days)":round(gap,1),"Last Defect":last.date(),"Predicted Next Defect":(last+pd.Timedelta(days=gap)).date()})

                if forecasts:
                    st.dataframe(pd.DataFrame(forecasts),use_container_width=True)
                elif selected_eq:
                    st.info("Forecast requires at least two notifications for the selected equipment.")

                # ========================================================
                # PDF DOWNLOAD
                # ========================================================

                st.subheader(f"📄 Download Detailed {selected_plant} Report")

                st.write(f"The PDF report below contains detailed analysis only for **{selected_plant}**.")

                if st.button(f"Generate {selected_plant} Report",type="primary"):

                    pdf = pdf_report(plant_df,selected_plant,forecasts)

                    st.download_button(f"⬇️ Download {selected_plant} Report",pdf,file_name=f"{selected_plant}_Report.pdf",mime="application/pdf")

            else:

                st.info("👆 Please select a plant above to view its detailed analysis.")
