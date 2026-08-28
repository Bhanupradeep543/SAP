import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import io
import re

from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, PageBreak
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="NTPC SAP Analysis",
    layout="wide"
)

st.title("🏭 NTPC SAP Notifications Analysis")


# ============================================================
# DEFECT PATTERNS
# ============================================================

patterns = {
    "Gland Leak": r"gland|galand|GLD",
    "Vibration": r"vibration|vib",
    "Bearing/Coupling": r"sound|bearing|brng|thrust",
    "NRV Passing": r"nrv",
    "Valve Issues": r"valve|vlv|v/v|bfv",
    "Oil Leakage": r"oil",
    "Reverse/Decoupled": r"reverse|decouple",
    "Pipe Leakage": r"pipe|line|hdr|header",
    "Overloading/Tripping": r"overload|OL|O/L|current|curren",
    "Pump Pressure": r"pr low|develop|pressure|devlp",
    "Choking": r"choke",
    "Jamming": r"jam"
}


# ============================================================
# DEFECT SUMMARY FUNCTION
# ============================================================

def defect_summary(df):

    result = []

    for name, pattern in patterns.items():

        count = df["Description"].str.contains(
            pattern,
            case=False,
            na=False,
            regex=True
        ).sum()

        result.append({
            "Defect Category": name,
            "Count": int(count)
        })

    result = pd.DataFrame(result)

    result = result.sort_values(
        "Count",
        ascending=False
    ).reset_index(drop=True)

    return result


# ============================================================
# YEAR-WISE DEFECT ANALYSIS
# ============================================================

def yearwise_defect_analysis(df):

    years = sorted(
        df["Notif.date"]
        .dropna()
        .dt.year
        .unique()
    )

    result = []

    for category, pattern in patterns.items():

        temp = df[
            df["Description"].str.contains(
                pattern,
                case=False,
                na=False,
                regex=True
            )
        ].copy()

        row = {
            "Defect Category": category
        }

        for year in years:

            count = (
                temp[temp["Notif.date"].dt.year == year]
                .shape[0]
            )

            row[str(year)] = int(count)

        result.append(row)

    return pd.DataFrame(result)


# ============================================================
# PDF TABLE STYLE
# ============================================================

def style_table(table):

    table.setStyle(
        TableStyle([

            # Header
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#404040")
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER"
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.black
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            ),

            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [
                    colors.white,
                    colors.HexColor("#F2F2F2")
                ]
            )
        ])
    )


# ============================================================
# PDF REPORT FUNCTION
# ============================================================

def pdf_report(
    data,
    plant_df,
    plant,
    forecasts=None
):

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=25,
        leftMargin=25,
        topMargin=25,
        bottomMargin=25
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        spaceAfter=15
    )

    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        fontSize=14,
        spaceBefore=10,
        spaceAfter=8
    )

    normal_style = ParagraphStyle(
        "NormalStyle",
        parent=styles["BodyText"],
        fontSize=9,
        leading=13
    )

    elements = []

    # ========================================================
    # TITLE
    # ========================================================

    elements.append(
        Paragraph(
            "NTPC SAP Notifications Analysis Report",
            title_style
        )
    )

    elements.append(
        Paragraph(
            f"<b>Plant:</b> {plant}",
            styles["Heading2"]
        )
    )

    elements.append(
        Paragraph(
            f"<b>Report Generated:</b> "
            f"{pd.Timestamp.now().strftime('%d-%m-%Y %H:%M')}",
            normal_style
        )
    )

    elements.append(Spacer(1, 15))


    # ========================================================
    # 1. PLANT SUMMARY
    # ========================================================

    elements.append(
        Paragraph(
            "1. Plant Summary",
            heading_style
        )
    )

    total_notifications = len(plant_df)

    total_equipment = plant_df["equipment"].nunique()

    first_date = (
        plant_df["Notif.date"].min()
        if plant_df["Notif.date"].notna().any()
        else None
    )

    last_date = (
        plant_df["Notif.date"].max()
        if plant_df["Notif.date"].notna().any()
        else None
    )

    years_count = (
        plant_df["Notif.date"]
        .dt.year
        .nunique()
    )

    summary_data = [
        ["Parameter", "Value"],
        ["Plant", plant],
        ["Total Notifications", total_notifications],
        ["Total Equipment", total_equipment],
        ["Number of Years", years_count],
        [
            "First Notification",
            first_date.strftime("%d-%m-%Y")
            if first_date is not None else "N/A"
        ],
        [
            "Last Notification",
            last_date.strftime("%d-%m-%Y")
            if last_date is not None else "N/A"
        ]
    ]

    table = Table(
        summary_data,
        colWidths=[220, 220]
    )

    style_table(table)

    elements.append(table)

    elements.append(Spacer(1, 15))


    # ========================================================
    # 2. PLANT-WISE SUMMARY
    # ========================================================

    elements.append(
        Paragraph(
            "2. Overall Plant-wise Notification Summary",
            heading_style
        )
    )

    plant_summary = (
        data.groupby("Plant")
        .size()
        .reset_index(name="Notifications")
        .sort_values(
            "Notifications",
            ascending=False
        )
    )

    plant_table_data = [
        ["Plant", "Notifications"]
    ] + plant_summary.values.tolist()

    table = Table(
        plant_table_data,
        repeatRows=1
    )

    style_table(table)

    elements.append(table)

    elements.append(PageBreak())


    # ========================================================
    # 3. DEFECT CATEGORY SUMMARY
    # ========================================================

    elements.append(
        Paragraph(
            f"3. Defect Category Analysis - {plant}",
            heading_style
        )
    )

    defect_df = defect_summary(plant_df)

    defect_df["Percentage"] = np.where(
        total_notifications > 0,
        (
            defect_df["Count"]
            / total_notifications
            * 100
        ).round(2),
        0
    )

    defect_table_data = [
        [
            "Defect Category",
            "Count",
            "%"
        ]
    ] + defect_df[
        [
            "Defect Category",
            "Count",
            "Percentage"
        ]
    ].values.tolist()

    table = Table(
        defect_table_data,
        repeatRows=1
    )

    style_table(table)

    elements.append(table)

    elements.append(Spacer(1, 15))


    # ========================================================
    # 4. YEAR-WISE DEFECT ANALYSIS
    # ========================================================

    elements.append(
        Paragraph(
            "4. Year-wise Defect Category Analysis",
            heading_style
        )
    )

    yearly_df = yearwise_defect_analysis(
        plant_df
    )

    yearly_table_data = [
        yearly_df.columns.tolist()
    ] + yearly_df.values.tolist()

    table = Table(
        yearly_table_data,
        repeatRows=1
    )

    style_table(table)

    elements.append(table)

    elements.append(PageBreak())


    # ========================================================
    # 5. DETAILED CATEGORY ANALYSIS
    # ========================================================

    elements.append(
        Paragraph(
            "5. Detailed Defect Category Analysis",
            heading_style
        )
    )

    years = sorted(
        plant_df["Notif.date"]
        .dropna()
        .dt.year
        .unique()
    )

    for category, pattern in patterns.items():

        category_df = plant_df[
            plant_df["Description"].str.contains(
                pattern,
                case=False,
                na=False,
                regex=True
            )
        ].copy()

        total_category = len(category_df)

        elements.append(
            Paragraph(
                f"<b>{category}</b> — "
                f"Total Notifications: {total_category}",
                normal_style
            )
        )

        if len(category_df) > 0:

            category_yearly = []

            for year in years:

                count = category_df[
                    category_df["Notif.date"].dt.year == year
                ].shape[0]

                category_yearly.append(
                    [str(year), int(count)]
                )

            category_table_data = [
                ["Year", "Notifications"]
            ] + category_yearly

            table = Table(
                category_table_data,
                colWidths=[100, 120]
            )

            style_table(table)

            elements.append(table)

        else:

            elements.append(
                Paragraph(
                    "No notifications found for this category.",
                    normal_style
                )
            )

        elements.append(Spacer(1, 10))


    # ========================================================
    # 6. EQUIPMENT-WISE ANALYSIS
    # ========================================================

    elements.append(PageBreak())

    elements.append(
        Paragraph(
            "6. Equipment-wise Notification Analysis",
            heading_style
        )
    )

    equipment_df = (
        plant_df["equipment"]
        .value_counts()
        .reset_index()
    )

    equipment_df.columns = [
        "Equipment",
        "Count"
    ]

    equipment_df[
        "Interval (weeks)"
    ] = np.where(
        equipment_df["Count"] > 0,
        (
            520
            / equipment_df["Count"]
        ).round().astype(int),
        0
    )

    equipment_df = equipment_df.head(20)

    equipment_table_data = [
        [
            "Equipment",
            "Count",
            "Interval (weeks)"
        ]
    ] + equipment_df.values.tolist()

    table = Table(
        equipment_table_data,
        repeatRows=1
    )

    style_table(table)

    elements.append(table)


    # ========================================================
    # 7. FORECAST
    # ========================================================

    if forecasts is not None and len(forecasts) > 0:

        elements.append(Spacer(1, 20))

        elements.append(
            Paragraph(
                "7. Equipment Defect Forecast",
                heading_style
            )
        )

        forecast_df = pd.DataFrame(
            forecasts
        )

        forecast_table_data = [
            forecast_df.columns.tolist()
        ] + forecast_df.values.tolist()

        table = Table(
            forecast_table_data,
            repeatRows=1
        )

        style_table(table)

        elements.append(table)


    # ========================================================
    # 8. MANAGEMENT ANALYSIS
    # ========================================================

    elements.append(PageBreak())

    elements.append(
        Paragraph(
            "8. Management-Level Detailed Analysis",
            heading_style
        )
    )

    # Highest defect
    if not defect_df.empty:

        highest = defect_df.iloc[0]

        lowest_nonzero = (
            defect_df[
                defect_df["Count"] > 0
            ]
            .sort_values("Count")
            .iloc[0]
            if not defect_df[
                defect_df["Count"] > 0
            ].empty
            else None
        )

        analysis_text = (
            f"<b>Key Finding 1:</b> "
            f"The highest number of notifications "
            f"is associated with <b>"
            f"{highest['Defect Category']}</b>, "
            f"with {int(highest['Count'])} notifications "
            f"({highest['Percentage']:.2f}% of total notifications)."
        )

        elements.append(
            Paragraph(
                analysis_text,
                normal_style
            )
        )

        elements.append(Spacer(1, 8))

        if lowest_nonzero is not None:

            elements.append(
                Paragraph(
                    f"<b>Key Finding 2:</b> "
                    f"Among categories having notifications, "
                    f"<b>{lowest_nonzero['Defect Category']}</b> "
                    f"has the lowest occurrence with "
                    f"{int(lowest_nonzero['Count'])} notifications.",
                    normal_style
                )
            )

            elements.append(Spacer(1, 8))


    # Equipment finding
    if not equipment_df.empty:

        top_equipment = equipment_df.iloc[0]

        elements.append(
            Paragraph(
                f"<b>Key Finding 3:</b> "
                f"The equipment with the highest number "
                f"of notifications is "
                f"<b>{top_equipment['Equipment']}</b>, "
                f"with {int(top_equipment['Count'])} notifications.",
                normal_style
            )
        )

        elements.append(Spacer(1, 8))


    # Year trend analysis
    if len(years) >= 2:

        elements.append(
            Paragraph(
                "<b>Key Finding 4:</b> "
                "The year-wise defect analysis should be "
                "used to identify increasing, decreasing and "
                "recurring defect patterns. Categories showing "
                "persistent or increasing notifications should "
                "be prioritised for RCA and preventive maintenance.",
                normal_style
            )
        )

        elements.append(Spacer(1, 8))


    elements.append(
        Paragraph(
            "<b>Recommended Action:</b> "
            "High-frequency defect categories and equipment "
            "should be prioritised for Root Cause Analysis (RCA), "
            "condition monitoring, preventive maintenance "
            "optimization and spare-parts planning. "
            "Recurring notifications should be reviewed for "
            "permanent corrective actions rather than repeated "
            "breakdown maintenance.",
            normal_style
        )
    )


    # ========================================================
    # BUILD PDF
    # ========================================================

    doc.build(elements)

    buffer.seek(0)

    return buffer


# ============================================================
# FILE UPLOAD
# ============================================================

files = st.file_uploader(
    "Upload Excel/CSV files from different plants",
    type=["xlsx", "csv"],
    accept_multiple_files=True
)


if files:

    # ========================================================
    # PLANT NAME ASSIGNMENT
    # ========================================================

    st.subheader("🏭 Assign Plant Name")

    file_data = []

    for i, f in enumerate(files):

        c1, c2 = st.columns([2, 1])

        with c1:

            st.write(
                f"📄 {f.name}"
            )

        with c2:

            plant = st.text_input(
                "Plant Name",
                key=f"plant{i}",
                placeholder="Korba"
            )

        if plant:

            file_data.append(
                (f, plant)
            )


    # ========================================================
    # READ FILES
    # ========================================================

    if file_data:

        frames = []

        for f, plant in file_data:

            try:

                if f.name.lower().endswith(".xlsx"):

                    d = pd.read_excel(
                        f,
                        engine="openpyxl"
                    )

                else:

                    d = pd.read_csv(f)

                d["Plant"] = plant

                frames.append(d)

            except Exception as e:

                st.error(
                    f"{f.name}: {e}"
                )


        # ====================================================
        # COMBINE DATA
        # ====================================================

        if frames:

            data = pd.concat(
                frames,
                ignore_index=True
            )


            # =================================================
            # REQUIRED COLUMNS
            # =================================================

            required = [
                "Notif.date",
                "equipment",
                "Description",
                "Functional Loc."
            ]

            missing = [
                c for c in required
                if c not in data.columns
            ]

            if missing:

                st.error(
                    f"Missing columns: {missing}"
                )

                st.stop()


            # =================================================
            # DATA CLEANING
            # =================================================

            data["Notif.date"] = pd.to_datetime(
                data["Notif.date"],
                format="%Y%m%d",
                errors="coerce"
            )

            for c in [
                "equipment",
                "Description",
                "Functional Loc."
            ]:

                data[c] = (
                    data[c]
                    .astype(str)
                )


            st.success(
                f"{len(data):,} notifications loaded "
                f"from {data['Plant'].nunique()} plants."
            )


            # =================================================
            # OVERALL DASHBOARD
            # =================================================

            st.header(
                "📊 Overall Dashboard"
            )

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "Total Notifications",
                f"{len(data):,}"
            )

            c2.metric(
                "Plants",
                data["Plant"].nunique()
            )

            c3.metric(
                "Equipment",
                data["equipment"].nunique()
            )

            c4.metric(
                "Years",
                data["Notif.date"]
                .dt.year
                .nunique()
            )


            # =================================================
            # PLANT SUMMARY
            # =================================================

            plant_summary = (
                data.groupby("Plant")
                .size()
                .reset_index(
                    name="Notifications"
                )
                .sort_values(
                    "Notifications",
                    ascending=False
                )
            )

            st.subheader(
                "🏭 Plant-wise Notifications"
            )

            st.dataframe(
                plant_summary,
                use_container_width=True
            )

            st.bar_chart(
                plant_summary.set_index(
                    "Plant"
                )
            )


            # =================================================
            # PLANT × DEFECT DASHBOARD
            # =================================================

            dashboard = []

            for plant in data["Plant"].unique():

                d = data[
                    data["Plant"] == plant
                ]

                row = {
                    "Plant": plant,
                    "Total": len(d)
                }

                for name, pattern in patterns.items():

                    row[name] = int(
                        d["Description"]
                        .str.contains(
                            pattern,
                            case=False,
                            na=False,
                            regex=True
                        )
                        .sum()
                    )

                dashboard.append(row)


            dashboard_df = pd.DataFrame(
                dashboard
            )

            st.subheader(
                "🔧 Plant-wise Defect Dashboard"
            )

            st.dataframe(
                dashboard_df,
                use_container_width=True
            )


            # =================================================
            # OVERALL DEFECT DISTRIBUTION
            # =================================================

            st.subheader(
                "📈 Overall Defect Distribution"
            )

            overall = defect_summary(
                data
            )

            st.dataframe(
                overall,
                use_container_width=True
            )

            st.bar_chart(
                overall.set_index(
                    "Defect Category"
                )
            )


            # =================================================
            # DETAILED PLANT ANALYSIS
            # =================================================

            st.header(
                "🔍 Detailed Plant Analysis"
            )

            selected_plant = st.selectbox(
                "Select Plant",
                sorted(
                    data["Plant"].unique()
                )
            )

            pdf_data = data[
                data["Plant"] == selected_plant
            ].copy()


            # =================================================
            # PLANT KPI
            # =================================================

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "Notifications",
                len(pdf_data)
            )

            c2.metric(
                "Equipment",
                pdf_data["equipment"].nunique()
            )

            c3.metric(
                "First Notification",
                (
                    str(
                        pdf_data["Notif.date"]
                        .min()
                        .date()
                    )
                    if pdf_data[
                        "Notif.date"
                    ].notna().any()
                    else "N/A"
                )
            )

            c4.metric(
                "Last Notification",
                (
                    str(
                        pdf_data["Notif.date"]
                        .max()
                        .date()
                    )
                    if pdf_data[
                        "Notif.date"
                    ].notna().any()
                    else "N/A"
                )
            )


            # =================================================
            # DEFECT ANALYSIS
            # =================================================

            st.subheader(
                f"📊 Defect Analysis - {selected_plant}"
            )

            detail = defect_summary(
                pdf_data
            )

            detail["%"] = np.where(
                len(pdf_data) > 0,
                (
                    detail["Count"]
                    / len(pdf_data)
                    * 100
                ).round(2),
                0
            )

            st.dataframe(
                detail,
                use_container_width=True
            )


            # =================================================
            # ALL CATEGORY YEAR-WISE TREND
            # =================================================

            st.subheader(
                "📅 Year-wise Defect Category Trends"
            )

            yearly_all = (
                yearwise_defect_analysis(
                    pdf_data
                )
            )

            st.dataframe(
                yearly_all,
                use_container_width=True
            )


            # =================================================
            # INDIVIDUAL CATEGORY TRENDS
            # =================================================

            st.markdown(
                "### 📈 Individual Category Trends"
            )

            years = sorted(
                pdf_data["Notif.date"]
                .dropna()
                .dt.year
                .unique()
            )

            for category, pattern in patterns.items():

                temp = pdf_data[
                    pdf_data["Description"]
                    .str.contains(
                        pattern,
                        case=False,
                        na=False,
                        regex=True
                    )
                ].copy()

                yearly = (
                    temp.groupby(
                        temp["Notif.date"].dt.year
                    )
                    .size()
                    .reindex(
                        years,
                        fill_value=0
                    )
                    .reset_index(
                        name="Count"
                    )
                )

                st.markdown(
                    f"#### 🔹 {category}"
                )

                total_category = len(temp)

                st.write(
                    f"**Total {category}: "
                    f"{total_category:,} notifications**"
                )

                if len(yearly) > 0:

                    st.bar_chart(
                        yearly.set_index(
                            "Notif.date"
                        )
                    )

                else:

                    st.info(
                        "No year-wise data available."
                    )


            # =================================================
            # EQUIPMENT ANALYSIS
            # =================================================

            st.subheader(
                "⚙️ Equipment-wise Notifications"
            )

            eq = (
                pdf_data["equipment"]
                .value_counts()
                .reset_index()
            )

            eq.columns = [
                "Equipment",
                "Count"
            ]

            eq["Interval (weeks)"] = np.where(
                eq["Count"] > 0,
                (
                    520
                    / eq["Count"]
                ).round().astype(int),
                0
            )

            st.dataframe(
                eq.head(20),
                use_container_width=True
            )


            # =================================================
            # FORECAST
            # =================================================

            st.subheader(
                "🔮 Equipment Defect Forecast"
            )

            selected_eq = st.multiselect(
                "Select Equipment for Forecast",
                eq["Equipment"].tolist(),
                key=f"eq_{selected_plant}"
            )

            forecasts = []

            for equipment in selected_eq:

                dates = (
                    pdf_data.loc[
                        pdf_data["equipment"]
                        == equipment,
                        "Notif.date"
                    ]
                    .dropna()
                    .sort_values()
                )

                if len(dates) > 1:

                    gap = (
                        dates.diff()
                        .dt.days
                        .dropna()
                        .mean()
                    )

                    last = dates.max()

                    predicted = (
                        last
                        + pd.Timedelta(
                            days=gap
                        )
                    )

                    forecasts.append({

                        "Equipment":
                            equipment,

                        "Defects":
                            len(dates),

                        "Average Gap (days)":
                            round(gap, 1),

                        "Last Defect":
                            last.date(),

                        "Predicted Next Defect":
                            predicted.date()
                    })


            if forecasts:

                st.dataframe(
                    pd.DataFrame(
                        forecasts
                    ),
                    use_container_width=True
                )

            elif selected_eq:

                st.info(
                    "Forecast requires at least "
                    "two notifications for the "
                    "selected equipment."
                )


            # =================================================
            # PDF REPORT
            # =================================================

            st.subheader(
                "📄 Detailed PDF Report"
            )

            st.write(
                "The PDF contains the complete plant analysis, "
                "all defect categories, year-wise trends, "
                "equipment analysis and management-level findings."
            )

            if st.button(
                "Generate PDF Report",
                type="primary"
            ):

                pdf = pdf_report(
                    data,
                    pdf_data,
                    selected_plant,
                    forecasts
                )

                st.download_button(
                    "⬇️ Download Detailed PDF Report",
                    pdf,
                    file_name=(
                        f"{selected_plant}"
                        f"_SAP_Detailed_Report.pdf"
                    ),
                    mime="application/pdf"
                )
