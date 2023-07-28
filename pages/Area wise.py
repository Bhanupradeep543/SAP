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
url = "https://raw.githubusercontent.com/Bhanupradeep543/SAP/master/SAPdata.xlsx"
data = pd.read_excel(url)
data=data[data['Main WorkCtr']!='OPRN']
data1=data[data['Description'].str.contains('PM ')]
data=data.drop(data[data['Description'].isin(data1['Description'])].index)
st.title('Area wise analysis')
st.subheader("Select the area for Analysis")
options = st.multiselect('Click on below',['BLR-1','BLR-2','TG-1','TG-2'])
g=options[0]
dict={'BLR-1':['10-HNC10','10-HNC20','10-HLB10','10-HLB20','10-HFD10','10-HFD20','10-HLD10','10-HLD20','10-HFV10','10-HFV20','10-HFV30','10-HFV40','10-HFV50','10-HFV60','10-HFV70','10-HFV80']
      ,'BLR-2':['20-HNC10','20-HNC20','20-HLB10','20-HLB20','20-HFD10','20-HFD20','20-HLD10','20-HLD20','20-HFV10','20-HFV20','20-HFV30','20-HFV40','20-HFV50','20-HFV60','20-HFV70','20-HFV80']
      ,'TG-1':'','TG-2':''}
def convert_df(df):
 return df.to_csv().encode('utf-8')
data2=data[data['Functional Loc.'].str.contains('|'.join(dict[g]))]
data2 = data2.drop(columns=['Notification','Order','Priority','User status','Req. start','Required End','Created By','System status','MaintenancePlan','Changed by'
                            ,'Changed On','MaintPlant','Reported by'])
st.subheader("Total defects in the above System")
st.write(data2.shape[0])
rp=data2['System'].value_counts()
st.subheader("TOP 20 repeated defects in the above System")
rp=data2['System'].value_counts().head(20)
st.write(rp)
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

#adding a download button to download csv file

