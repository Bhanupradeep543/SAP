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
st.subheader("Select the Equipment/System")
options = st.multiselect('Select the planner Group',['IDF-1A','IDF-1B','IDF-2A','IDF-2B','FDF-1A','FDF-1B','FDF-2A','FDF-2B','PAF-1A','PAF-1B','PAF-2A','PAF-2B'
                                                     ,'APH-1A','APH-1B','APH-2A','APH-2B','MILL-1A','MILL-2A','MILL-1B','MILL-1C'
                                                    ,'MILL-2B','MILL-2C','MILL-1D','MILL-2D','MILL-2E','MILL-1E','MILL-1F','MILL-2F'
                                                    ,'MILL-2G','MILL-1G','TDBFP-1A','TDBFP-1B','TDBFP-2A','TDBFP-2B','MDBFP','U1 sootblowing system','U2 sootblowing system'])
g=options[0]
dict={'IDF-2A':'20-HNC10','IDF-1A':'10-HNC10','IDF-1B':'10-HNC20','IDF-2B':'20-HNC20','FDF-1A':'10-HLB10'
      ,'FDF-1B':'10-HLB20','FDF-2A':'20-HLB10','FDF-2B':'20-HLB20','PAF-1A':'10-HFD10','PAF-1B':'10-HFD20'
      ,'PAF-2A':'20-HFD10','PAF-2B':'20-HFD20','APH-1A':'10-HLD10','APH-1B':'10-HLD20','APH-2A':'20-HLD10'
      ,'APH-2B':'20-HLD20','MILL-1A':'10-HFV10','MILL-2A':'20-HFV10','MILL-1B':'10-HFV20','MILL-1C':'10-HFV30'
      ,'MILL-2B':'20-HFV20','MILL-2C':'20-HFV30','MILL-1D':'10-HFV40','MILL-2D':'20-HFV40','MILL-2E':'20-HFV50'
      ,'MILL-1E':'10-HFV50','MILL-1F':'10-HFV60','MILL-2F':'20-HFV60','MILL-2G':'20-HFV70','MILL-1G':'10-HFV70'
      ,'MILL-2H':'20-HFV80','MILL-1H':'10-HFV80','TDBFP-1A':'10-LAA20','TDBFP-1B':'10-LAA30'
      ,'TDBFP-2A':'20-LAA20','TDBFP-2B':'20-LAA30','U1 MDBFP':'10-LAA10','U2 MDBFP':'20-LAA10','U1 sootblowing system':'10-HCB51'
      ,'U2 sootblowing system':'20-HCB51'}
data2=data[data['Functional Loc.'].str.contains(dict[g])]
data2 = data2.drop(columns=['Notification','Order','Priority','User status','Req. start','Required End','Created By','System status','MaintenancePlan','Changed by'
                            ,'Changed On','MaintPlant','Reported by'])
st.write(data2)
cs = convert_df(data2) 
st.download_button(label="Download",data=cs,file_name='Repeated notifications.csv',mime='text/csv')
st.subheader("TOP 5 repeated defects in the above equipment")
rp=data2['System'].value_counts().head(5)
if g=='U1 sootblowing system':
   data3=data2[data2['Description'].str.contains('struck ')]
   data4=data2[data2['Description'].str.contains('overload ')]
   data5=data2[data2['Description'].str.contains('leak ')]
   st.write("Sootblowers Srtucking defect")
   st.write(data3['System'].value_counts())
   st.write("Sootblowers overload defect")
   st.write(data4['System'].value_counts())
   st.write("Sootblowers flange leak")
   st.write(data5['System'].value_counts()) 

#adding a download button to download csv file

