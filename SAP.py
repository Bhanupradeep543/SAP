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
st.subheader('Top 20 Repeated notifications in the station')
data=data[data['equipment']!='KORBA STATION COMMON']
repeat_defects = (data.groupby(['equipment']).size().reset_index(name='Count'))
repeated = repeat_defects[repeat_defects['Count'] > 50]
repeated = repeated.sort_values(by=['Count', 'equipment'], ascending=[False, True]).head(20)
st.write(repeated)
options = st.multiselect('select the stage', ['STAGE-1', 'STAGE-2', 'STAGE-3'])                                                     
dict={'STAGE-1':['S1COM'],'STAGE-2':['S2COM'],'STAGE-3':['S3COM']}
g=options[0]
data2=data[data['Functional Loc.'].str.contains(dict[g])]
repeat_defects = (data2.groupby(['equipment']).size().reset_index(name='Count'))
st.subheader("Total defects in the above stage")
st.write(data2.shape[0])
repeated = repeat_defects[repeat_defects['Count'] > 20]
repeated = repeated.sort_values(by=['Count', 'equipment'], ascending=[False, True]).head(10)
st.subheader("TOP 10 repeated defects in the selected stage")
st.write(repeated)
