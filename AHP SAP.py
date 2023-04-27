#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import pickle
from sklearn import preprocessing
from scipy import stats
import numpy as np
import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt
data = pd.DataFrame(pd.read_excel("AHP data.xlsx"))
data1=data[data['Description'].str.contains('PM ')]
data=data.drop(data[data['Description'].isin(data1['Description'])].index)
print(data.shape)


# In[2]:


print(data.info())


# In[3]:


print(data['System'].value_counts().head(20))


# In[4]:


print(data['Planner group'].value_counts())


# In[19]:


data1=data[data['Description'].str.contains('seal')]
print(data1.shape)
print(data1['System'].value_counts())

