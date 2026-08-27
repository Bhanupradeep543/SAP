import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import io
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="NTPC SAP Reliability Dashboard",layout="wide")
st.title("🏭 NTPC SAP Notifications Analysis")

# ============================================================
# DEFECT CATEGORIES
# ============================================================

patterns={"Gland Leak":r"gland|galand|GLD","Vibration":r"vibration|vib","Bearing/Coupling":r"sound|bearing|brng|thrust","NRV Passing":r"nrv","Valve Issues":r"valve|vlv|v/v|bfv","Oil Leakage":r"oil","Reverse/Decoupled":r"reverse|decouple","Pipe Leakage":r"pipe|line|hdr|header","Overloading/Tripping":r"overload|OL|O/L|current|curren","Pump Pressure":r"pr low|develop|pressure|devlp","Choking":r"choke","Jamming":r"jam"}

# ============================================================
# SYSTEM CATEGORIES
# Add more systems here whenever required
# ============================================================

systems={"CT Fans":r"CT FAN|CT FAN|COOLING TOWER FAN|CTF","CW Pumps":r"CW PUMP|CWP|CIRCULATING WATER PUMP","BFP":r"BFP|BOILER FEED PUMP","CEP":r"CEP|CONDENSATE EXTRACTION PUMP","ID Fans":r"ID FAN|IDF|INDUCED DRAFT FAN","FD Fans":r"FD FAN|FDF|FORCED DRAFT FAN","PA Fans":r"PA FAN|PAF|PRIMARY AIR FAN","Coal Mills":r"MILL|COAL MILL","Ash Handling":r"ASH|AHP|ASH HANDLING","Air Compressors":r"COMPRESSOR|AIR COMPRESSOR"}

# ============================================================
# DEFECT SUMMARY FUNCTION
# ============================================================

def defect_summary(df):
    return pd.DataFrame([{"Defect Category":n,"Count":df["Description"].str.contains(p,case=False,na=False).sum()} for n,p in patterns.items()])

# ============================================================
# SYSTEM CLASSIFICATION
# ============================================================

def classify_system(row):
    text=f"{row.get('equipment','')} {row.get('Functional Loc.','')}".upper()
    for system,pattern in systems.items():
        if pd.Series([text]).str.contains(pattern,case=False,regex=True).iloc[0]:
            return system
    return "Other"

# ============================================================
# PDF REPORT
# ============================================================

def make_pdf(data,plant_df,plant,common_df,graph_files):
    b=io.BytesIO()
    doc=SimpleDocTemplate(b,pagesize=landscape(A4),rightMargin=25,leftMargin=25,topMargin=25,bottomMargin=25)
    styles=getSampleStyleSheet()
    E=[Paragraph("NTPC SAP Notifications Reliability Analysis",styles["Title"]),Paragraph(f"Detailed Plant: {plant}",styles["Heading2"]),Spacer(1,12)]

    # Plant summary
    ps=data.groupby("Plant").size().reset_index(name="Notifications")
    E += [Paragraph("Plant-wise Notification Summary",styles["Heading2"]),Table([["Plant","Notifications"]]+ps.values.tolist(),repeatRows=1),Spacer(1,15)]

    # Plant defect matrix
    E.append(Paragraph("Plant-wise Defect Category Comparison",styles["Heading2"]))
    mat=[]
    for p in data["Plant"].unique():
        d=data[data["Plant"]==p]
        mat.append([p,len(d)]+[d["Description"].str.contains(x,case=False,na=False).sum() for x in patterns.values()])
    E.append(Table([["Plant","Total"]+list(patterns.keys())]+mat,repeatRows=1))
    E.append(PageBreak())

    # Common systems
    E.append(Paragraph("Common System Comparison",styles["Heading2"]))
    if not common_df.empty:E.append(Table([list(common_df.columns)]+common_df.values.tolist(),repeatRows=1))
    else:E.append(Paragraph("No system was found in all uploaded plants.",styles["Normal"]))
    E.append(PageBreak())

    # Selected plant
    E.append(Paragraph(f"Detailed Analysis - {plant}",styles["Heading2"]))
    ds=defect_summary(plant_df)
    ds["%"]=round(ds["Count"]/len(plant_df)*100,2) if len(plant_df)>0 else 0
    E.append(Table([list(ds.columns)]+ds.values.tolist(),repeatRows=1))
    E.append(PageBreak())

    # All graphs
    for title,path in graph_files:
        E.append(Paragraph(title,styles["Heading2"]))
        E.append(Image(path,width=8.5*inch,height=4.7*inch))
        E.append(Spacer(1,10))

    # Equipment
    eq=plant_df["equipment"].value_counts().head(20).reset_index()
    eq.columns=["Equipment","Count"]
    E.append(PageBreak())
    E.append(Paragraph("Top 20 Equipment",styles["Heading2"]))
    E.append(Table([["Equipment","Count"]]+eq.values.tolist(),repeatRows=1))

    # Table formatting
    for obj in E:
        if isinstance(obj,Table):
            obj.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.grey),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),0.4,colors.black),("ALIGN",(1,1),(-1,-1),"CENTER"),("FONTSIZE",(0,0),(-1,-1),7)]))
    doc.build(E)
    b.seek(0)
    return b

# ============================================================
# FILE UPLOAD
# ============================================================

files=st.file_uploader("Upload SAP defect files from different plants",type=["xlsx","csv"],accept_multiple_files=True)

if files:
    st.subheader("🏭 Assign Plant Name to Each File")
    file_data=[]
    for i,f in enumerate(files):
        c1,c2=st.columns([2,1])
        with c1:st.write(f"📄 {f.name}")
        with c2:plant=st.text_input("Plant Name",key=f"plant{i}",placeholder="Korba")
        if plant:file_data.append((f,plant))

    if file_data:
        frames=[]
        for f,plant in file_data:
            try:
                d=pd.read_excel(f,engine="openpyxl") if f.name.lower().endswith(".xlsx") else pd.read_csv(f)
                d["Plant"]=plant
                frames.append(d)
            except Exception as e:st.error(f"Error reading {f.name}: {e}")

        if frames:
            data=pd.concat(frames,ignore_index=True)
            required=["Notif.date","equipment","Description","Functional Loc."]
            missing=[c for c in required if c not in data.columns]
            if missing:st.error(f"Missing columns: {missing}");st.stop()

            data["Notif.date"]=pd.to_datetime(data["Notif.date"],format="%Y%m%d",errors="coerce")
            for c in ["equipment","Description","Functional Loc."]:data[c]=data[c].fillna("").astype(str)

            # ==================================================
            # SYSTEM CLASSIFICATION
            # ==================================================

            data["System"]=data.apply(classify_system,axis=1)

            st.success(f"{len(data):,} notifications loaded from {data['Plant'].nunique()} plants.")

            # ==================================================
            # KPI DASHBOARD
            # ==================================================

            st.header("📊 Overall Dashboard")
            c1,c2,c3,c4=st.columns(4)
            c1.metric("Total Notifications",f"{len(data):,}")
            c2.metric("Plants",data["Plant"].nunique())
            c3.metric("Equipment",data["equipment"].nunique())
            c4.metric("Systems",data["System"].nunique())

            # ==================================================
            # PLANT-WISE DEFECT DASHBOARD
            # ==================================================

            st.subheader("🏭 Plant-wise Defect Dashboard")
            rows=[]
            for p in data["Plant"].unique():
                d=data[data["Plant"]==p]
                rows.append([p,len(d)]+[d["Description"].str.contains(x,case=False,na=False).sum() for x in patterns.values()])
            plant_defect=pd.DataFrame(rows,columns=["Plant","Total"]+list(patterns.keys()))

            def highlight_extreme(s):
                if s.name=="Plant" or s.name=="Total":return [""]*len(s)
                m=s.min();M=s.max()
                return ["background-color:#ff9999" if v==M and M!=m else "background-color:#99ff99" if v==m and M!=m else "" for v in s]

            st.dataframe(plant_defect.style.apply(highlight_extreme,axis=0),use_container_width=True)

            st.caption("🔴 Red = Highest defects in that category | 🟢 Green = Lowest defects in that category")

            # ==================================================
            # OVERALL DEFECT GRAPH
            # ==================================================

            overall=defect_summary(data).sort_values("Count",ascending=False)
            st.subheader("🔧 Overall Defect Distribution")
            st.dataframe(overall,use_container_width=True)
            st.bar_chart(overall.set_index("Defect Category"))

            # ==================================================
            # COMMON SYSTEM COMPARISON
            # ==================================================

            st.header("⚙️ Common System Comparison Across Plants")

            system_counts=data.groupby(["System","Plant"]).size().unstack(fill_value=0)
            common_systems=system_counts.columns if len(system_counts)==0 else system_counts.loc[:,(system_counts>0).all()].index

            # Correct common-system identification
            common_list=[s for s in data["System"].unique() if s!="Other" and data.loc[data["System"]==s,"Plant"].nunique()==data["Plant"].nunique()]

            if common_list:
                common_df=system_counts.loc[common_list].reset_index()
                st.dataframe(common_df,use_container_width=True)
                st.bar_chart(common_df.set_index("System"))
            else:
                common_df=pd.DataFrame()
                st.info("No predefined system is available in all uploaded plants.")

            # ==================================================
            # DETAILED PLANT ANALYSIS
            # ==================================================

            st.header("🔍 Detailed Plant Analysis")
            selected_plant=st.selectbox("Select Plant",sorted(data["Plant"].unique()))
            plant_df=data[data["Plant"]==selected_plant].copy()

            c1,c2,c3,c4=st.columns(4)
            c1.metric("Notifications",len(plant_df))
            c2.metric("Equipment",plant_df["equipment"].nunique())
            c3.metric("Systems",plant_df["System"].nunique())
            c4.metric("Defect Categories",len(patterns))

            # ==================================================
            # ALL DEFECT CATEGORIES
            # ==================================================

            st.subheader(f"📊 Complete Defect Analysis - {selected_plant}")
            detail=defect_summary(plant_df)
            detail["%"]=round(detail["Count"]/len(plant_df)*100,2) if len(plant_df)>0 else 0
            st.dataframe(detail,use_container_width=True)
            st.bar_chart(detail.set_index("Defect Category")["Count"])

            # ==================================================
            # YEAR-WISE ALL DEFECT GRAPHS
            # ==================================================

            st.subheader("📅 Year-wise Defect Analysis")
            graph_files=[]

            for name,pattern in patterns.items():
                temp=plant_df[plant_df["Description"].str.contains(pattern,case=False,na=False)].copy()
                temp["Year"]=temp["Notif.date"].dt.year
                yearly=temp.groupby("Year").size()
                st.write(f"**{name} — {len(temp)} notifications**")
                if not yearly.empty:
                    st.bar_chart(yearly)
                    fig,ax=plt.subplots(figsize=(10,4))
                    ax.bar(yearly.index.astype(str),yearly.values)
                    ax.set_title(f"{selected_plant} - Year-wise {name}")
                    ax.set_xlabel("Year")
                    ax.set_ylabel("Defect Count")
                    fig.tight_layout()
                    path=f"/tmp/{selected_plant}_{name.replace('/','_')}.png"
                    fig.savefig(path,dpi=120)
                    plt.close(fig)
                    graph_files.append((name,path))

            # ==================================================
            # SYSTEM-WISE ANALYSIS WITHIN SELECTED PLANT
            # ==================================================

            st.subheader("⚙️ System-wise Notifications")
            system_plant=plant_df.groupby("System").size().reset_index(name="Notifications").sort_values("Notifications",ascending=False)
            st.dataframe(system_plant,use_container_width=True)

            # ==================================================
            # EQUIPMENT ANALYSIS
            # ==================================================

            st.subheader("🔧 Equipment-wise Notifications")
            eq=plant_df["equipment"].value_counts().reset_index()
            eq.columns=["Equipment","Count"]
            eq["Average Interval (weeks)"]=(520/eq["Count"]).round().astype(int)
            st.dataframe(eq.head(20),use_container_width=True)

            # ==================================================
            # FORECAST
            # ==================================================

            st.subheader("🔮 Equipment Defect Forecast")
            selected_eq=st.multiselect("Select equipment for forecast",eq["Equipment"].head(20).tolist())
            forecast=[]
            for e in selected_eq:
                dates=plant_df.loc[plant_df["equipment"]==e,"Notif.date"].dropna().sort_values()
                if len(dates)>1:
                    gap=dates.diff().dt.days.dropna().mean();last=dates.max()
                    forecast.append({"Equipment":e,"Defects":len(dates),"Avg Gap (days)":round(gap,1),"Last Defect":last.date(),"Predicted Next Defect":(last+pd.Timedelta(days=gap)).date()})
            if forecast:st.dataframe(pd.DataFrame(forecast),use_container_width=True)
            elif selected_eq:st.info("At least two notifications are required for forecasting.")

            # ==================================================
            # PDF REPORT
            # ==================================================

            st.divider()
            st.subheader("📄 Complete PDF Report")

            if st.button("Generate Complete PDF Report",type="primary"):
                pdf=make_pdf(data,plant_df,selected_plant,common_df,graph_files)
                st.download_button("⬇️ Download PDF Report",pdf,file_name=f"{selected_plant}_SAP_Complete_Report.pdf",mime="application/pdf")
