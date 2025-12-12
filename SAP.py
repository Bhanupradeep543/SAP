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
import random 
import base64
st.title("NTPC SAP Notifications Analysis")
uploaded_file = st.file_uploader("Upload your defect data (Excel/CSV)",type=["xlsx", "xls", "csv"])
data = pd.read_excel(uploaded_file)
st.success("File loaded successfully")
data['Notif.date'] = pd.to_datetime(data['Notif.date'], format='%Y%m%d')
data1 = data[data['Main WorkCtr'] == 'M400CWCT']
st.subheader('Total SAP notifications considered for analysis')
st.subheader(data1.shape[0])
st.subheader('Top 20 Repeated equipment notifications')
data=data[data['equipment']!='KORBA STATION COMMON']
repeat_defects = (data.groupby(['equipment']).size().reset_index(name='Count'))
repeated = repeat_defects[repeat_defects['Count'] > 50]
repeated = repeated.sort_values(by=['Count', 'equipment'], ascending=[False, True]).head(20)
st.write(repeated)
# Hardcoded keywords
KEYWORDS = ["1017-S1COM-ACW-ACL","1017-S1COM-ACW-ACT","1017-S1COM-CLT-T01","1017-S1COM-CLT-T02","1017-S1COM-CLT-T03","1017-S1COM-CTS",
"1017-S1COM-CWS","1017-S1COM-CWS-SWP","1017-S1COM-CWS-TWS","1017-S2COM-CLT-T4A","1017-S2COM-CLT-T4B","1017-S2COM-CLT-T5A","1017-S2COM-CLT-T5B",
"1017-S2COM-CLT-T6A","1017-S2COM-CLT-T6B","1017-S2COM-CTS","1017-S2COM-CWS-CHL","1017-S2COM-CWS","1017-S2COM-CWS-SWP","1017-S2COM-CWS-TS",
"1017-S3COM-CLT-T7A","1017-S3COM-CLT-T7B","1017-S3COM-CWS"]
# Mapping keywords → final display name
KEYWORD_MAP = {"1017-S1COM-ACW-ACL":"ADD.CLARIFIED PUMP SYSTEM","1017-S1COM-ACW-ACT":"ADD.CLARIFIED COOLING TOWERS","1017-S1COM-CLT-T01":"ST-1 COOLING TOWER-1","1017-S1COM-CLT-T02":"ST-1 COOLING TOWER-2",
"1017-S1COM-CLT-T03":"ST-1 COOLING TOWER-3","1017-S1COM-CTS":"ST-1 CT PUMPS SYSTEM","1017-S1COM-CWS":"ST-1 CW SYSTEM","1017-S1COM-CWS-SWP":"ST-1 SCREEN WASH PUMPS SYSTEM","1017-S1COM-CWS-TWS":"ST-1 TWS SYSTEM",
"1017-S2COM-CLT-T4A":"ST-2 COOLING TOWER 4A","1017-S2COM-CLT-T4B":"ST-2 COOLING TOWER 4B","1017-S2COM-CLT-T5A":"ST-2 COOLING TOWER 5A",
"1017-S2COM-CLT-T5B":"ST-2 COOLING TOWER 5B","1017-S2COM-CLT-T6A":"ST-2 COOLING TOWER 6A","1017-S2COM-CLT-T6B":"ST-2 COOLING TOWER 6B",
"1017-S2COM-CTS":"ST-2 CT PUMPS SYSTEM","1017-S2COM-CWS-CHL":"ST-2 CW CHLORINATION SYSTEM","1017-S2COM-CWS":"ST-2 CW SYSTEM","1017-S2COM-CWS-SWP":"ST-2 SCREEN WASH PUMP SYSTEM",
"1017-S2COM-CWS-TS":"ST-2 TWS SYSTEM","1017-S3COM-CLT-T7A":"ST-3 COOLING TOWER 7A","1017-S3COM-CLT-T7B":"ST-3 COOLING TOWER 7B","1017-S3COM-CWS":"ST-3 CW SYSTEM"}
COLUMN_NAME = "Functional Loc."
# Process column
col_data = data[COLUMN_NAME].astype(str)
results = []
# Count occurrences for each keyword
for kw in KEYWORDS:
    count = col_data.str.contains(kw).sum()
    final_name = KEYWORD_MAP.get(kw, kw)
    results.append({"Keyword": final_name,"Count": count})
    # Convert to dataframe
result_df = pd.DataFrame(results)
 # Total count for % calculation
total = result_df["Count"].sum()
result_df["Percentage"] = (result_df["Count"] / total * 100).astype(int)
# Sort descending
result_df = result_df.sort_values(by="Count", ascending=False).reset_index(drop=True)
    # Display final result
st.write("system wise no.of defects in last 10 years")
st.dataframe(result_df)
# PC code without errors
keywords = {"Stage-1": "S1COM","Stage-2": "S2COM","Stage-3": "S3COM" }
selected = st.multiselect("Select the stage:", list(keywords.keys()))
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
     
  data4=data2[data2['Description'].str.contains('Vibration|vibration|VIBRATION|vib|VIB')]
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
 
  data7=data2[data2['Description'].str.contains('valve|VALVE|vlv|VLV|Valve|v/v|BFV|bfv')]
  data7["Year"] = data7['Notif.date'].dt.year
  st.write("no.of valve issues in the selected stage",data7.shape[0])
  yearly_count = data7.groupby("Year")['Notif.date'].count().reset_index()
  yearly_count.rename(columns={'Notif.date': "Valve issues"}, inplace=True)
  st.subheader("📅 Year-wise Valve issues")
  st.bar_chart(data=yearly_count, x="Year", y="Valve issues")

  data8=data2[data2['Description'].str.contains('oil|OIL|Oil')]
  data8["Year"] = data8['Notif.date'].dt.year
  st.write("no.of oil leak/ oil top up issues in the selected stage",data8.shape[0])
  yearly_count = data8.groupby("Year")['Notif.date'].count().reset_index()
  yearly_count.rename(columns={'Notif.date': "Oil leaks/ oil top up issues"}, inplace=True)
  st.subheader("📅 Year-wise Oil leaks/ oil top up issues")
  st.bar_chart(data=yearly_count, x="Year", y="Oil leaks/ oil top up issues")

  data9=data2[data2['Description'].str.contains('reverse|REVERSE|Reverse|Decouple|decouple|DECOUPLE')]
  data9["Year"] = data9['Notif.date'].dt.year
  st.write("no.of pump/Fan shaft Decoupled/reverse rotational issues in the selected stage",data9.shape[0])
  yearly_count = data9.groupby("Year")['Notif.date'].count().reset_index()
  yearly_count.rename(columns={'Notif.date': "pump/Fan shaft jam/reverse rotational issues"}, inplace=True)
  st.subheader("📅 Year-wise pump/Fan shaft Decoupled/reverse rotational issues")
  st.bar_chart(data=yearly_count, x="Year", y="pump/Fan shaft jam/reverse rotational issues")
     
  data10=data2[data2['Description'].str.contains('pipe|PIPE|LINE|Line|line|Pipe')]
  data10["Year"] = data10['Notif.date'].dt.year
  st.write("no.of Pipe leakage issues in the selected stage",data10.shape[0])
  yearly_count = data9.groupby("Year")['Notif.date'].count().reset_index()
  yearly_count.rename(columns={'Notif.date': "Pipe leakage issues"}, inplace=True)
  st.subheader("📅 Year-wise Pipe leakage issues")
  st.bar_chart(data=yearly_count, x="Year", y="Pipe leakage issues")
  
  data11=data2[data2['Description'].str.contains('overload|OVERLOAD|OL|Overload|O/L|o/l|current|CURRENT|Current')]
  data11["Year"] = data11['Notif.date'].dt.year
  st.write("no.of Over loading/ tripping issues in the selected stage",data11.shape[0])
  yearly_count = data11.groupby("Year")['Notif.date'].count().reset_index()
  yearly_count.rename(columns={'Notif.date': "Over loading/ tripping issues"}, inplace=True)
  st.subheader("📅 Year-wise Over loading/ tripping issues")
  st.bar_chart(data=yearly_count, x="Year", y="Over loading/ tripping issues")

  data12=data2[data2['Description'].str.contains('pr low|PR LOW|DEVELOP|develop|Develop|pressure|PRESSURE')]
  data12["Year"] = data12['Notif.date'].dt.year
  st.write("no.of pump pressure related issues in the selected stage",data12.shape[0])
  yearly_count = data12.groupby("Year")['Notif.date'].count().reset_index()
  yearly_count.rename(columns={'Notif.date': "pump pressure issues"}, inplace=True)
  st.subheader("📅 Year-wise pump pressure issues")
  st.bar_chart(data=yearly_count, x="Year", y="pump pressure issues")

  data13=data2[data2['Description'].str.contains('CHOKE|choke|Choke')]
  data13["Year"] = data13['Notif.date'].dt.year
  st.write("no.of Line/ CT Nozzles chokage issues in the selected stage",data13.shape[0])
  yearly_count = data13.groupby("Year")['Notif.date'].count().reset_index()
  yearly_count.rename(columns={'Notif.date': "Line/ CT Nozzles chokage issues"}, inplace=True)
  st.subheader("📅 Year-wise Line/ CT Nozzles chokage issues")
  st.bar_chart(data=yearly_count, x="Year", y="Line/ CT Nozzles chokage issues")

  tc=data3.shape[0]+data4.shape[0]+data5.shape[0]+data6.shape[0]+data7.shape[0]+data8.shape[0]+data9.shape[0]+data10.shape[0]+data11.shape[0]+data12.shape[0]+data13.shape[0]
  per=(tc/data2.shape[0])*100
  per=int(per)
  st.write("% of notifications divided into various categories",per)
     
  date_col = "Notif.date"
  equip_col = "equipment"
  # Convert to datetime
  data2[date_col] = pd.to_datetime(data2[date_col], errors='coerce')
  data2 = data2.dropna(subset=[date_col, equip_col])
  # Convert equipment name to string to avoid dtype mismatch
  data2[equip_col] = data2[equip_col].astype(str)
  # Equipment frequency table
  equip_count = data2[equip_col].value_counts().reset_index()
  equip_count.columns = [equip_col, 'Defect_Count']
  # Show equipment list with counts
  st.subheader("⚙️ Equipment-wise defect count in selected stage")
  st.dataframe(equip_count)

selected_equips = st.multiselect("Select equipment(s) to forecast:",options=equip_count[equip_count['Defect_Count'] > 0][equip_col].tolist(),
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
    result = pd.DataFrame(forecast_results)
st.subheader("📅 Forecasted Next Defect Dates")
st.dataframe(result) 


