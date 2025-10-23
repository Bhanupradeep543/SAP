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
data1=data[data['Main WorkCtr']=='M400CWCT']
st.subheader('Total SAP notifications considered for analysis')
st.subheader(data1.shape[0])
st.subheader('Top 20 Repeated notifications ')
data=data[data['equipment']!='KORBA STATION COMMON']
repeat_defects = (data.groupby(['equipment']).size().reset_index(name='Count'))
repeated = repeat_defects[repeat_defects['Count'] > 50]

repeated = repeated.sort_values(by=['Count', 'equipment'], ascending=[False, True]).head(20)

st.write(repeated)
#options = st.multiselect('select the stage', ['STAGE-1', 'STAGE-2', 'STAGE-3'])                                                     
#g=options[0]
#dict={'STAGE-1':[S1COM],'STAGE-2':[S2COM],'STAGE-3':[S3COM]}

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

