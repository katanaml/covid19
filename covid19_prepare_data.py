
# coding: utf-8

# In[1]:


import requests
from datetime import datetime
import pandas as pd


# In[2]:


def build_country_data(country):
    res = []
    keys = country.get('timeline').get('cases').keys()
    for key in keys:
        target_entry = {}
        target_entry['Report_Date'] = key
        country_name = country.get('country')
        if country.get('province') != None:
            country_name = country_name + '_' + country.get('province')
        target_entry[country_name + '_cases'] = country.get('timeline').get('cases').get(key)
        target_entry[country_name + '_deaths'] = country.get('timeline').get('deaths').get(key)
        target_entry[country_name + '_recovered'] = country.get('timeline').get('recovered').get(key)
        res.append(target_entry)
    return res


# In[11]:


def build_covid19_data():
    request_str = 'https://corona.lmao.ninja/v2/historical'
    response = requests.get(request_str)
    json_data = response.json() if response and response.status_code == 200 else None
    
    df = None
    for country in json_data:
        res = build_country_data(country)
        if df is None:
            df = pd.DataFrame(res)
            df.index = pd.DatetimeIndex(df['Report_Date'])
            df = df.drop('Report_Date', 1)
            df = df.sort_values(by=['Report_Date'])
        else:
            df_new = pd.DataFrame(res)
            df_new.index = pd.DatetimeIndex(df_new['Report_Date'])
            df_new = df_new.drop('Report_Date', 1)
            df_new = df_new.sort_values(by=['Report_Date'])
            df = df.merge(df_new, left_index=True, right_index=True)
    
    df.to_csv('data/covid19_data.csv')
    return df


# In[12]:


# df = build_covid19_data()

