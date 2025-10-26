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
import streamlit as st
from twilio.rest import Client
import random
import streamlit as st

# ------------------------
# Default credentials
# ------------------------
USERNAME = "bhanu"
PASSWORD = "m400cwct"

# ------------------------
# Streamlit login
# ------------------------
st.title("Simple Login Page")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    if username == USERNAME and password == PASSWORD:
        st.success(f"Welcome {username}!")
        st.write("You are now logged in. This is your protected page.")
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

                date_col = st.selectbox("Select Date column", data2.columns)
                equip_col = st.selectbox("Select Equipment column", data2.columns)

                # Convert to datetime
                data2[date_col] = pd.to_datetime(data2[date_col], errors='coerce')
                data2 = data2.dropna(subset=[date_col, equip_col])

                # Convert equipment name to string to avoid dtype mismatch
                data2[equip_col] = data2[equip_col].astype(str)

                # Equipment frequency table
                equip_count = data2[equip_col].value_counts().reset_index()
                equip_count.columns = [equip_col, 'Defect_Count']

                # Show equipment list with counts
                st.subheader("⚙️ Equipment-wise defect frequency")
                st.dataframe(equip_count)

                #    Let user pick one or more equipments
                selected_equips = st.multiselect(
                    "Select equipment(s) to forecast:",
                    options=equip_count[equip_count['Defect_Count'] > 0][equip_col].tolist(),
                    help="You can select multiple equipments for prediction.")

                forecast_results = []

                if selected_equips:
                    for eq in selected_equips:
                        eq_data = data2[data2[equip_col] == eq].sort_values(by=date_col)
                        eq_dates = eq_data[date_col].dropna().sort_values()

                    if len(eq_dates) > 1:
                        # Calculate gaps between defects
                        gaps = eq_dates.diff().dt.days.dropna()

                        avg_gap = gaps.mean()
                        last_date = eq_dates.max()
                        next_pred_date = last_date + pd.Timedelta(days=avg_gap)

                        forecast_results.append({"Equipment": eq,"Total_Defects": len(eq_dates),"Average_Gap_(days)": round(avg_gap, 1),
                         "Last_Defect_Date": last_date.date(),"Predicted_Next_Defect": next_pred_date.date()})

                    if forecast_results:
                        result_df = pd.DataFrame(forecast_results)
                        st.subheader("📅 Forecasted Next Defect Dates")
                        st.dataframe(result_df)
        

    else:
            st.error("Invalid username or password")
