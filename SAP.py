#!/usr/bin/env python
# coding: utf-8

# In[ ]:
import pandas as pd
import pickle
from sklearn import preprocessing
from scipy import stats
import numpy as np
import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt
import streamlit as st
import io
from datetime import datetime

st.subheader("""NTPC SAP Notifications """) # Tittle addition
url = "https://raw.githubusercontent.com/Bhanupradeep543/SAP/master/korba_defects.xlsx"
data = pd.read_excel(url)
data['Notif.date'] = pd.to_datetime(data['Notif.date'], format='%Y%m%d')
data1=data[data['Main WorkCtr']=='M400CWCT']
st.subheader('Total SAP notifications considered for analysis')
st.subheader(data1.shape[0])
st.subheader('Top 20 Repeated notifications in the station')
data=data[data['equipment']!='KORBA STATION COMMON']
repeat_defects = (data.groupby(['equipment']).size().reset_index(name='Count'))
repeated = repeat_defects[repeat_defects['Count'] > 50]
repeated = repeated.sort_values(by=['Count', 'equipment'], ascending=[False, True]).head(20)
st.write(repeated)
keywords = {
    "Stage-1": "S1COM","Stage-2": "S2COM","Stage-3": "S3COM","Boiler": "BLR_SYS","Turbine": "TRB_SYS","Cooling Water": "CW_SYS"
}
selected = st.multiselect("Select the systems:", list(keywords.keys()))
if selected:
     selected_keywords = [keywords[s] for s in selected]
     for k in selected_keywords:
        data2=data[data['Functional Loc.'].str.contains(k)]
        st.subheader("Total defects in the selected stage")
        st.write(data2.shape[0])
        repeat_defects = (data2.groupby(['equipment']).size().reset_index(name='Count'))     
        repeated = repeat_defects[repeat_defects['Count'] > 10]
        repeated = repeated.sort_values(by=['Count', 'equipment'], ascending=[False, True]).head(10)
        st.subheader("TOP 10 repeated defects in the selected stage")
        df = pd.DataFrame(repeated)
        multiplier = 520
        df['each notification interval in terms of weeks'] = ((multiplier)/df['Count']).round().astype(int)
        st.write(df)
        st.subheader("equipment wise defects in the selected stage")
        repeat_defects = (data2.groupby(['equipment']).size().reset_index(name='Count'))
        repeated = repeat_defects[repeat_defects['Count'] > 1]
        repeated = repeated.sort_values(by=['Count', 'equipment'], ascending=[False, True])
        df1 = pd.DataFrame(repeated)
        st.write(df1)
        
        data3=data2[data2['Description'].str.contains('gland|GLAND|Gland|galand')]
        data3["Year"] = data3['Notif.date'].dt.year
        st.write("no.of gland leaks in the selected stage",data3.shape[0])
        yearly_count = data3.groupby("Year")['Notif.date'].count().reset_index()
        yearly_count.rename(columns={'Notif.date': "gland leak"}, inplace=True)
        st.subheader("📅 Year-wise gland leaks")
        st.bar_chart(data=yearly_count, x="Year", y="gland leak")      
        
        data4=data2[data2['Description'].str.contains('Vibration|vibration|VIBRATION')]
        data4["Year"] = data4['Notif.date'].dt.year
        st.write("no.of vibrational issues in the selected stage",data4.shape[0])
        yearly_count = data4.groupby("Year")['Notif.date'].count().reset_index()
        yearly_count.rename(columns={'Notif.date': "vibrational issues"}, inplace=True)
        st.subheader("📅 Year-wise vibrational issues")
        st.bar_chart(data=yearly_count, x="Year", y="vibrational issues")    
        
        data5=data2[data2['Description'].str.contains('sound|SOUND|Sound|bearing|BEARING|Bearing|brng|BRNG|thrust|THRUST|Thrust')]
        data5["Year"] = data5['Notif.date'].dt.year
        st.write("no.of bearing/coupling issues in the selected stage",data5.shape[0])
        yearly_count = data5.groupby("Year")['Notif.date'].count().reset_index()
        yearly_count.rename(columns={'Notif.date': "bearing/coupling issues"}, inplace=True)
        st.subheader("📅 Year-wise bearing/coupling issues")
        st.bar_chart(data=yearly_count, x="Year", y="bearing/coupling issues") 
        
        data6=data2[data2['Description'].str.contains('nrv|NRV|Nrv')]
        data6["Year"] = data6['Notif.date'].dt.year
        st.write("no.of NRV passing issues in the selected stage",data6.shape[0])
        yearly_count = data6.groupby("Year")['Notif.date'].count().reset_index()
        yearly_count.rename(columns={'Notif.date': "NRV passing"}, inplace=True)
        st.subheader("📅 Year-wise NRV passings")
        st.bar_chart(data=yearly_count, x="Year", y="NRV passing")

        data7=data2[data2['Description'].str.contains('valve|VALVE|vlv|VLV|Valve')]
        data7["Year"] = data7['Notif.date'].dt.year
        st.write("no.of valve issues in the selected stage",data7.shape[0])
        yearly_count = data7.groupby("Year")['Notif.date'].count().reset_index()
        yearly_count.rename(columns={'Notif.date': "Valve issues"}, inplace=True)
        st.subheader("📅 Year-wise Valve issues")
        st.bar_chart(data=yearly_count, x="Year", y="Valve issues")

        date_col = data2['Notif.date']
        equip_col=data2['equipment']
         
        # Count occurrences per equipment
        equip_count = data2['equipment'].value_counts().reset_index()
        equip_count.columns = [equip_col, 'Count']
        # Filter equipments with >30 defects
        frequent_equip = equip_count[equip_count['Count'] > 30][equip_col].tolist()
        st.write(f"Equipments with more than 30 defects: {len(frequent_equip)}")
        forecast_results = []
        for eq in frequent_equip:
           eq_data = data2[data2['equipment'] == eq].sort_values(by=date_col)
           eq_dates = eq_data[date_col].dropna().sort_values()
         # Compute intervals between defects
        gaps = eq_dates.diff().dt.days.dropna()
        if len(gaps) > 0:
            avg_gap = gaps.mean()
            last_date = eq_dates.max()
            next_pred_date = last_date + pd.Timedelta(days=avg_gap)

            forecast_results.append({
                "Equipment": eq,
                "Total_Defects": len(eq_dates),
                "Average_Gap_(days)": round(avg_gap, 1),
                "Last_Defect_Date": last_date.date(),
                "Predicted_Next_Defect": next_pred_date.date()
            })

        result_df = pd.DataFrame(forecast_results)
        st.subheader("📅 Forecasted Next Defect Dates")
        st.dataframe(result_df)

        
