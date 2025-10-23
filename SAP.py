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
data=data[data['Main WorkCtr']!='M400CWCT']
data1=data[data['Description'].str.contains('PM ')]
data=data.drop(data[data['Description'].isin(data1['Description'])].index)
st.subheader('Total SAP notifications considered for analysis')
st.subheader(data.shape[0])

options = st.multiselect('select the stage',['STAGE-1','STAGE-2','STAGE-3'])                                                     ])
g=options[0]
dict={'STAGE-1':[S1COM],'STAGE-2':[S2COM],'STAGE-3':[S3COM]}
#st.subheader("Select the date range for notifications") 
#d = st.date_input("From", )
#e = st.date_input("TO", )

#column_name = 'System'
#word_counts = data[column_name].value_counts()
#repeated_words = word_counts[word_counts > 15]
#grouped = data.groupby(column_name)
#repeated_rows = grouped.apply(lambda x: x[x[column_name].isin(repeated_words.index)])
#st.subheader("Top 100 repeated notifications from SEIL P1")
#rp1=repeated_rows['System'].value_counts().head(100)
#st.write(rp1)
def convert_df(df):
 return df.to_csv().encode('utf-8')
#cs = convert_df(repeated_rows) 
#adding a download button to download csv file
#st.download_button(label="Download",data=cs,file_name='Repeated notifications.csv',mime='text/csv')
#st.subheader("Select the Planner group for obtaining repeated notifications")
#options = st.multiselect('Select the planner Group',['CIA','CIB','CIC','CID','CIN','CIV','CNI','EAP','EBP','EBR','MAP','MBP','MBM','MTM'])
#c=options[0]
#st.write(c)
#st.subheader("Max. notifications Reported by")
#st.bar_chart(data['Reported by'].value_counts().head(10))
#st.subheader("Max. notifications Planner group wise")
#st.bar_chart(data['Planner group'].value_counts().head(7))
#st.subheader("User status of notification")
#st.write(data['User status'].value_counts().head())
#st.subheader("Repeated notifications Planner group wise")
#b=data[data['Planner group']==c]
#rp=b['System'].value_counts().head(20)
#st.write(rp)
#cs = convert_df(rp) 
#adding a download button to download csv file
#st.download_button(label="Download",data=cs,file_name='Repeated notifications.csv',mime='text/csv')
data2=data[data['Functional Loc.'].str.contains(dict[g])]
data2 = data2.drop(columns=['Notification','Order','Priority','User status','Req. start','Required End','Created By','System status','MaintenancePlan','Changed by'
                            ,'Changed On','MaintPlant','Reported by'])
st.subheader("Total defects in the above System/equipment")
rp=data2['System'].value_counts()
st.subheader("TOP 5 repeated defects in the above System/equipment")
rp=data2['System'].value_counts().head(5)
st.write(rp)
st.subheader("No.of defefcts planner group wise")
fig, ax = plt.subplots()
ax.pie(data2['Main WorkCtr'].value_counts(),autopct='%1.1f%%')
ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

# Display the chart in Streamlit
st.pyplot(fig)
st.write(data2['Main WorkCtr'].value_counts())
data2['Created On']=pd.to_datetime(data2['Created On'])
data2['Created On']=data2['Created On'].dt.strftime('%m/%Y')

st.bar_chart(data2['Created On'].value_counts().head(7))
st.write(data2)
cs = convert_df(data2) 
st.download_button(label="Download",data=cs,file_name='Repeated notifications.csv',mime='text/csv')

if g=='U1 sootblowing system':
   data3=data2[data2['Description'].str.contains('struck|strucked|stucked|STRUCK|STUCK')]
   data4=data2[data2['Description'].str.contains('overload|olr')]
   data5=data2[data2['Description'].str.contains('leak|LEAK')]
   data6=data2[data2['Description'].str.contains('lance|LANCE|tube')]
   st.write("Sootblowers Srtucking defect")
   st.write(data3['System'].value_counts())
   st.write("Sootblowers overload defect")
   st.write(data4['System'].value_counts())
   st.write("Sootblowers flange leak")
   st.write(data5['System'].value_counts())
   st.write("Sootblowers lance tube defects")
   st.write(data6['System'].value_counts())
  
elif g=='U2 sootblowing system':
   data3=data2[data2['Description'].str.contains('struck|strucked|stucked|STRUCK|STUCK')]
   data4=data2[data2['Description'].str.contains('overload|olr')]
   data5=data2[data2['Description'].str.contains('leak|LEAK')]
   data6=data2[data2['Description'].str.contains('lance|LANCE|tube')]
   st.write("Sootblowers Srtucking defect")
   st.write(data3['System'].value_counts())
   st.write("Sootblowers overload defect")
   st.write(data4['System'].value_counts())
   st.write("Sootblowers flange leak")
   st.write(data5['System'].value_counts())
   st.write("Sootblowers lance tube defects")
   st.write(data6['System'].value_counts())

#adding a download button to download csv file

