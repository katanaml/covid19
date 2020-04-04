
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
from fbprophet import Prophet
import pickle
import math
import scipy.optimize as optim
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

import covid19_prepare_data as prepare_data

import logging
logging.getLogger('fbprophet').setLevel(logging.WARNING)


# In[7]:


def fetch_data():
    prepare_data.build_covid19_data()


# In[3]:


# Define funcion with the coefficients to estimate
def func_logistic(t, a, b, c):
    return c / (1 + a * np.exp(-b*t))


# In[10]:


def detect_growth():
    countries_processed = 0
    countries_stabilized = 0
    countries_increasing = 0
    
    df = pd.read_csv('data/covid19_data.csv', parse_dates=True)
    columns = df.columns.values
    for column in columns:
        if column.endswith('_cases'):
            data = pd.DataFrame(df[column].values)
            
            data = data.reset_index(drop=False)
            data.columns = ['Timestep', 'Total Cases']
            
            # Randomly initialize the coefficients
            p0 = np.random.exponential(size=3)

            # Set min bound 0 on all coefficients, and set different max bounds for each coefficient
            bounds = (0, [100000., 1000., 1000000000.])

            # Convert pd.Series to np.Array and use Scipy's curve fit to find the best Nonlinear Least Squares coefficients
            x = np.array(data['Timestep']) + 1
            y = np.array(data['Total Cases'])
            
            try:
                (a,b,c),cov = optim.curve_fit(func_logistic, x, y, bounds=bounds, p0=p0, maxfev=1000000)
                
                # The time step at which the growth is fastest
                t_fastest = np.log(a) / b
                i_fastest = func_logistic(t_fastest, a, b, c)
                
                res_df = df[['Report_Date', column]].copy()
                res_df['fastest_grow_day'] = t_fastest
                res_df['fastest_grow_value'] = i_fastest
                res_df['growth_stabilized'] = t_fastest <= x[-1]
                res_df['timestep'] = x
                res_df['res_func_logistic'] = func_logistic(x, a, b, c)
            
                if t_fastest <= x[-1]:
                    print('Growth stabilized:', column, '| Fastest grow day:', t_fastest, '| Infections:', i_fastest)
                    res_df['cap'] = func_logistic(x[-1] + 10, a, b, c)
                    countries_stabilized += 1
                else:
                    print('Growth increasing:', column, '| Fastest grow day:', t_fastest, '| Infections:', i_fastest)
                    res_df['cap'] = func_logistic(i_fastest + 10, a, b, c)
                    countries_increasing += 1
                
                countries_processed += 1
                
                res_df.to_csv('data/covid19_processed_data_' + column + '.csv')
            except RuntimeError:
                print('No fit found for: ', column)
                
    d = {'countries_processed': [countries_processed], 'countries_stabilized': [countries_stabilized], 'countries_increasing': [countries_increasing]}
    df_c = pd.DataFrame(data=d)
    df_c.to_csv('data/covid19_stats_countries.csv')

# detect_growth()


# In[6]:


def build_model(country):
    df = pd.read_csv('data/covid19_processed_data_' + country + '.csv', parse_dates=True)
    df_ = df.copy()
    df = df[['Report_Date', country, 'cap']].dropna()
    
    df.columns = ['ds', 'y', 'cap']
    
    m = Prophet(growth="logistic")
    m.fit(df)

    future = m.make_future_dataframe(periods=20)
    future['cap'] = df['cap'].iloc[0]

    forecast = m.predict(future)
    
    res_df = forecast.set_index('ds')[['yhat', 'yhat_lower', 'yhat_upper']].join(df.set_index('ds').y).reset_index()
    res_df['current_date'] = df['ds'].iloc[-1]
    res_df['fastest_growth_day'] = df_['fastest_grow_day'].iloc[-1]
    res_df['growth_stabilized'] = df_['growth_stabilized'].iloc[-1]
    res_df['current_day'] = df_['timestep'].iloc[-1]
    res_df['cap'] = df['cap'].iloc[0]
    
    res_df.to_csv('data/covid19_forecast_data_' + country + '.csv')
    
    print('Processed:', country)
    
#     fig1 = m.plot(forecast)
#     fig1.set_size_inches(18.5, 8.5)
#     datenow = datetime(2020, 4, 1)
#     dateend = datenow + timedelta(days=20)
#     datestart = dateend - timedelta(days=71)
#     plt.xlim([datestart, dateend])
#     plt.title("COVID19 forecast: " + country, fontsize=20)
#     plt.xlabel("Day", fontsize=20)
#     plt.ylabel("Infections", fontsize=20)
#     plt.axvline(datenow, color="k", linestyle=":")
#     plt.show()
    
#     print(res_df[['ds', 'y', 'yhat', 'yhat_lower', 'yhat_upper', 'current_date', 'fastest_growth_day', 'growth_stabilized', 'current_day']].tail(30))
    
# build_model('Lithuania_cases')


# In[21]:


def calculate_forecast():
    df = pd.read_csv('data/covid19_data.csv', parse_dates=True)
    columns = df.columns.values
    for column in columns:
        if column.endswith('_cases'):
            build_model(column)
    print('Forecast calculation completed')
    
# calculate_forecast()

