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
             background: url("https://www.google.com/imgres?imgurl=https%3A%2F%2Fupload.wikimedia.org%2Fwikipedia%2Fcommons%2Fthumb%2F5%2F59%2FSAP_2011_logo.svg%2F1200px-SAP_2011_logo.svg.png&imgrefurl=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FSAP&tbnid=PV_gS_R4dwZfaM&vet=12ahUKEwjL9YyEifn6AhVz_jgGHayaBbsQMygAegUIARDfAQ..i&docid=403En1J1CPN8VM&w=1200&h=593&q=SAP&ved=2ahUKEwjL9YyEifn6AhVz_jgGHayaBbsQMygAegUIARDfAQ");
             background-size: cover}}
         </style>""",unsafe_allow_html=True)
st.write("""# SEIL SAP Notification Dashboard """) # Tittle addition
st.subheader("Select the Options Below")

# adding upload button for giving test data input to model
data_file = st.file_uploader("Upload SAP EXCEL file",type=['xlsx'])

if st.button("Process"):
    if data_file is not None:
        file_details = {"Filename":data_file.name,"FileType":data_file.type,"FileSize":data_file.size}
        data_file.to_csv ("sap.csv", index = None, header=True)
        data=pd.DataFrame(pd.read_csv("sap.csv"))
        st.subheader('total data points')
        st.dataframe(data.shape)


