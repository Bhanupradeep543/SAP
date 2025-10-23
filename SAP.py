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
        repeat_defects = (data2.groupby(['equipment']).size().reset_index(name='Count'))
        st.subheader("Total defects in the above stage")
        st.write(data2.shape[0])
        repeated = repeat_defects[repeat_defects['Count'] > 20]
        repeated = repeated.sort_values(by=['Count', 'equipment'], ascending=[False, True]).head(10)
        st.subheader("TOP 10 repeated defects in the selected stage")
        # Calculate defect frequency
        repeated = repeated.sort_values('Notif.date')
        # calculate difference in days
        deltas = repeated['Notif.date'].diff().dt.days.dropna()
        if len(deltas) > 0:
            avg_gap = deltas.mean()
        else:
            avg_gap = None  # only one notification
        
    avg_df = pd.DataFrame(avg_gap).sort_values('Avg_Days_Between_Notifications')
    
    st.subheader("📊 Average Duration Between Notifications")
    st.dataframe(avg_df)

        
     

