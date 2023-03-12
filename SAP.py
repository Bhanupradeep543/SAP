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
st.write("""# SEIL SAP Notifications """) # Tittle addition
#st.subheader("Select the date range for notifications") 
#d = st.date_input("From", )
#e = st.date_input("TO", )
url = "https://raw.githubusercontent.com/Bhanupradeep543/SAP/master/SAPdata.xlsx"
data = pd.read_excel(url)
data=data[data['Main WorkCtr']!='OPRN']
data1=data[data['Description'].str.contains('PM ')]
data=data.drop(data[data['Description'].isin(data1['Description'])].index)
st.subheader('Total notifications')
st.subheader(data.shape[0])
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
st.subheader("Select the Equipment")
options = st.multiselect('Select the planner Group',['IDF-1A','IDF-1B','IDF-2A','IDF-2B','FDF-1A','FDF-1B','FDF-2A','FDF-2B','PAF-1A','PAF-1B','PAF-2A','PAF-2B'
                                                     ,'APH-1A','APH-1B','APH-2A','APH-2B','MILL-1A','MILL-2A','MILL-1B','MILL-1C'
                                                    ,'MILL-2B','MILL-2C','MILL-1D','MILL-2D','MILL-2E','MILL-1E','MILL-1F','MILL-2F'
                                                    ,'MILL-2G','MILL-1G','TDBFP-1A','TDBFP-1B','TDBFP-2A','TDBFP-2B','MDBFP'])
g=options[0]
st.write(g)
dict={'IDF-2A':'20-HNC10','IDF-1A':'20-HNC10'}
data2=data[data['Functional Loc.'].str.contains(dict[g])]
del data2[data2.columns[0,1,2,3]]
st.write(data2)
cs = convert_df(data2) 
#adding a download button to download csv file
st.download_button(label="Download",data=cs,file_name='Repeated notifications.csv',mime='text/csv')
