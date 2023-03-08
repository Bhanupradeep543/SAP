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
# choosing the image for application background directly from web URL
st.markdown(f"""<style>.stApp {{                        
             background: url("https://www.intouch-quality.com/hubfs/quality-defects-ft-lg.jpg");
             background-size: cover}}
         </style>""",unsafe_allow_html=True)
st.write("""# SEIL SAP Notification Dashboard """) # Tittle addition
st.subheader("Select the date range for notifications") 
d = st.date_input("From", )
e = st.date_input("TO", )
st.subheader("Select the Planner group for obtaining repeated notifications")
options = st.multiselect('Select the planner Group',['CIA','CIB','CIC','CID','CIN','CIV','CNI','EAP','EBP','EBR','MAP','MBP','MBM','MTM'])
c=options[0]
st.write(c)
url=
data = pd.read_excel(url)
data=data[data['Main WorkCtr']!='OPRN']
data1=data[data['Description'].str.contains('PM ')]
data=data.drop(data[data['Description'].isin(data1['Description'])].index)
file_details = {"Filename":data_file.name,"FileType":data_file.type,"FileSize":data_file.size}
st.subheader('Total notifications')
st.write(data.shape[0])
#st.subheader("Max. notifications Reported by")
#st.bar_chart(data['Reported by'].value_counts().head(10))
#st.subheader("Max. notifications Planner group wise")
#st.bar_chart(data['Planner group'].value_counts().head(7))
#st.subheader("User status of notification")
#st.write(data['User status'].value_counts().head())
st.subheader("Repeated notifications Planner group wise")
b=data[data['Planner group']==c]
rp=b['System'].value_counts().head(20)
st.write(rp)
column_name = 'System'
word_counts = data[column_name].value_counts()
repeated_words = word_counts[word_counts > 15]
grouped = data.groupby(column_name)
repeated_rows = grouped.apply(lambda x: x[x[column_name].isin(repeated_words.index)])
st.subheader("Top 100 repeated notifications from SEIL P1")
rp1=repeated_rows['System'].value_counts().head(100)
st.write(rp1)
#def convert_df(df):
#return df.to_csv().encode('utf-8')
#cs = convert_df(repeated_rows) 
#adding a download button to download csv file
#st.download_button(label="Download",data=cs,file_name='Repeated notifications.csv',mime='text/csv')
for i in range(b.shape[0]):
   plngrp['Created On']=pd.to_datetime(pd.Series(plngrp['Created On']))
   plngrp['Created On']=plngrp['Created On'].dt.strftime('%Y/%m')
   st.bar_chart(plngrp['Created On'].value_counts().head(30))
   data['Created On']=pd.to_datetime(data['Created On']).dt.date
   newdata=pd.DataFrame()
for i in range(data.shape[0]):
  if (data['Created On'][i]>=d) and (data['Created On'][i]<=e) :
    newdata=newdata.append(data.iloc[i])
    st.subheader("Repeated notifications in mentioned dates")
    a=newdata.iloc[:,13].value_counts().head(300)
    st.write(a)
def convert_df(df):
  return df.to_csv().encode('utf-8')
csv = convert_df(a) # calling the function to convert the output file into CSV
#adding a download button to download csv file
st.download_button(label="Download",data=csv,file_name='Repeated notifications.csv',mime='text/csv')
