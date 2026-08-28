import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import io, re
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="NTPC SAP Analysis", layout="wide")
st.title("🏭 NTPC SAP Notifications Analysis")

patterns = {"Gland Leak":r"gland|galand|GLD","Vibration":r"vibration|vib","Bearing/Coupling":r"sound|bearing|brng|thrust","NRV Passing":r"nrv","Valve Issues":r"valve|vlv|v/v|bfv","Oil Leakage":r"oil","Reverse/Decoupled":r"reverse|decouple","Pipe Leakage":r"pipe|line|hdr|header","Overloading/Tripping":r"overload|OL|O/L|current|curren","Pump Pressure":r"pr low|develop|pressure|devlp","Choking":r"choke","Jamming":r"jam"}

def defect_summary(df):
    return pd.DataFrame([{"Defect Category":n,"Count":df["Description"].str.contains(p,case=False,na=False).sum()} for n,p in patterns.items()]).sort_values("Count",ascending=False)

def pdf_report(data,plant_df,plant):
    b=io.BytesIO(); doc=SimpleDocTemplate(b,pagesize=landscape(A4)); styles=getSampleStyleSheet(); elements=[Paragraph("NTPC SAP Notifications Analysis Report",styles["Title"]),Paragraph(f"Plant: {plant}",styles["Heading2"]),Spacer(1,15)]
    ps=data.groupby("Plant").size().reset_index(name="Notifications"); elements.append(Paragraph("Plant-wise Summary",styles["Heading2"])); elements.append(Table([["Plant","Notifications"]]+ps.values.tolist(),repeatRows=1))
    ds=defect_summary(plant_df); elements.append(Spacer(1,15)); elements.append(Paragraph("Defect Category Summary",styles["Heading2"])); elements.append(Table([["Defect Category","Count"]]+ds.values.tolist(),repeatRows=1))
    eq=plant_df["equipment"].value_counts().head(20).reset_index(); eq.columns=["Equipment","Count"]; elements.append(Spacer(1,15)); elements.append(Paragraph("Top 20 Equipment",styles["Heading2"])); elements.append(Table([["Equipment","Count"]]+eq.values.tolist(),repeatRows=1))
    for t in elements[1:]:
        if isinstance(t,Table): t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.grey),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),0.5,colors.black)]))
    doc.build(elements); b.seek(0); return b

files=st.file_uploader("Upload Excel/CSV files from different plants",type=["xlsx","csv"],accept_multiple_files=True)

if files:
    st.subheader("🏭 Assign Plant Name")
    file_data=[]
    for i,f in enumerate(files):
        c1,c2=st.columns([2,1])
        with c1: st.write(f"📄 {f.name}")
        with c2: plant=st.text_input("Plant Name",key=f"plant{i}",placeholder="Korba")
        if plant: file_data.append((f,plant))

    if file_data:
        frames=[]
        for f,plant in file_data:
            try:
                d=pd.read_excel(f,engine="openpyxl") if f.name.endswith(".xlsx") else pd.read_csv(f)
                d["Plant"]=plant; frames.append(d)
            except Exception as e: st.error(f"{f.name}: {e}")

        if frames:
            data=pd.concat(frames,ignore_index=True)
            required=["Notif.date","equipment","Description","Functional Loc."]
            missing=[c for c in required if c not in data.columns]
            if missing: st.error(f"Missing columns: {missing}"); st.stop()

            data["Notif.date"]=pd.to_datetime(data["Notif.date"],format="%Y%m%d",errors="coerce")
            for c in ["equipment","Description","Functional Loc."]: data[c]=data[c].astype(str)

            st.success(f"{len(data):,} notifications loaded from {data['Plant'].nunique()} plants.")

            # ==================== OVERALL DASHBOARD ====================
            st.header("📊 Overall Dashboard")
            c1,c2,c3,c4=st.columns(4)
            c1.metric("Total Notifications",f"{len(data):,}")
            c2.metric("Plants",data["Plant"].nunique())
            c3.metric("Equipment",data["equipment"].nunique())
            c4.metric("Years",data["Notif.date"].dt.year.nunique())

            plant_summary=data.groupby("Plant").size().reset_index(name="Notifications").sort_values("Notifications",ascending=False)
            st.subheader("🏭 Plant-wise Notifications")
            st.dataframe(plant_summary,use_container_width=True)
            st.bar_chart(plant_summary.set_index("Plant"))

            # ==================== PLANT × DEFECT ====================
            dashboard=[]
            for plant in data["Plant"].unique():
                d=data[data["Plant"]==plant]; row={"Plant":plant,"Total":len(d)}
                row.update({n:d["Description"].str.contains(p,case=False,na=False).sum() for n,p in patterns.items()}); dashboard.append(row)
            dashboard_df=pd.DataFrame(dashboard)
            st.subheader("🔧 Plant-wise Defect Dashboard")
            st.dataframe(dashboard_df,use_container_width=True)

            st.subheader("📈 Overall Defect Distribution")
            overall=defect_summary(data)
            st.dataframe(overall,use_container_width=True)
            st.bar_chart(overall.set_index("Defect Category"))

            # ==================== PLANT SELECTION ====================
            st.header("🔍 Detailed Plant Analysis")
            selected_plant=st.selectbox("Select Plant",sorted(data["Plant"].unique()))
            pdf_data=data[data["Plant"]==selected_plant].copy()

            c1,c2,c3,c4=st.columns(4)
            c1.metric("Notifications",len(pdf_data))
            c2.metric("Equipment",pdf_data["equipment"].nunique())
            c3.metric("First Notification",str(pdf_data["Notif.date"].min().date()) if pdf_data["Notif.date"].notna().any() else "N/A")
            c4.metric("Last Notification",str(pdf_data["Notif.date"].max().date()) if pdf_data["Notif.date"].notna().any() else "N/A")

            # ==================== DEFECT ANALYSIS ====================
            st.subheader(f"📊 Defect Analysis - {selected_plant}")
            detail=defect_summary(pdf_data)
            detail["%"]=round(detail["Count"]/len(pdf_data)*100,2) if len(pdf_data)>0 else 0
            st.dataframe(detail,use_container_width=True)

            # ==================== YEAR-WISE DEFECT ====================
            st.subheader("📅 Year-wise Defect Analysis")
            selected_defect=st.selectbox("Select Defect Category",list(patterns.keys()))
            temp=pdf_data[pdf_data["Description"].str.contains(patterns[selected_defect],case=False,na=False)].copy()
            yearly=temp.groupby(temp["Notif.date"].dt.year).size().reset_index(name="Count")
            st.write(f"Total {selected_defect}: {len(temp)}")
            st.bar_chart(yearly.set_index("Notif.date"))

            # ==================== EQUIPMENT ====================
            st.subheader("⚙️ Equipment-wise Notifications")
            eq=pdf_data["equipment"].value_counts().reset_index()
            eq.columns=["Equipment","Count"]
            eq["Interval (weeks)"]=(520/eq["Count"]).round().astype(int)
            st.dataframe(eq.head(20),use_container_width=True)

            # ==================== FORECAST ====================
            st.subheader("🔮 Equipment Defect Forecast")
            selected_eq=st.multiselect("Select Equipment",eq["Equipment"].tolist(),key=f"eq_{selected_plant}")
            forecasts=[]
            for equipment in selected_eq:
                dates=pdf_data.loc[pdf_data["equipment"]==equipment,"Notif.date"].dropna().sort_values()
                if len(dates)>1:
                    gap=dates.diff().dt.days.dropna().mean(); last=dates.max()
                    forecasts.append({"Equipment":equipment,"Defects":len(dates),"Average Gap (days)":round(gap,1),"Last Defect":last.date(),"Predicted Next Defect":(last+pd.Timedelta(days=gap)).date()})
            if forecasts: st.dataframe(pd.DataFrame(forecasts),use_container_width=True)
            elif selected_eq: st.info("Forecast requires at least two notifications for the selected equipment.")

            # ==================== PDF ====================
            st.subheader("📄 PDF Report")
            if st.button("Generate PDF Report",type="primary"):
                pdf=pdf_report(data,pdf_data,selected_plant)
                st.download_button("⬇️ Download PDF",pdf,file_name=f"{selected_plant}_SAP_Report.pdf",mime="application/pdf")
