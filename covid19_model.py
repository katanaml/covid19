
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


# In[2]:


def fetch_data():
    prepare_data.build_covid19_data()


# In[3]:


# Define function with the coefficients to estimate
def func_logistic(t, a, b, c):
    return c / (1 + a * np.exp(-b*t))


# In[4]:


# Hill sigmoidal function
def func_hill(t, a, b, c):
    return a * np.power(t, b) / (np.power(c, b) + np.power(t, b)) 


# In[21]:


def detect_growth(input_file, output_file, backtesting):
    countries_processed = 0
    countries_stabilized = 0
    countries_increasing = 0
    
    countries_list = []
    
    df = pd.read_csv(input_file, parse_dates=True)
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
                (a,b,c),cov = optim.curve_fit(func_logistic, x, y, bounds=bounds, p0=p0, maxfev=100000)
                
                # The time step at which the growth is fastest
                t_fastest = np.log(a) / b
                i_fastest = func_logistic(t_fastest, a, b, c)
                
                res_df = df[['Report_Date', column]].copy()
                
                if backtesting == False:
                    country = column.rsplit('_', 1)[0]
                    res_df['active_patients'] = df[column] - df[country + '_deaths'] - df[country + '_recovered']
                
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
                countries_list.append(column)
                
                res_df.to_csv(output_file + column + '.csv')
            except RuntimeError:
                print('No fit found for: ', column)
                
    if backtesting == False:
        d = {'countries_processed': [countries_processed], 'countries_stabilized': [countries_stabilized], 'countries_increasing': [countries_increasing]}
        df_c = pd.DataFrame(data=d)
        df_c.to_csv('data/covid19_stats_countries.csv')

        df_countries = pd.DataFrame(countries_list)
        df_countries.to_csv('data/covid19_countries_list.csv')

# detect_growth('data/covid19_data.csv', 'data/covid19_processed_data_', False)
# detect_growth('data/covid19_data_backtesting.csv', 'data/covid19_processed_backtesting_data_', True)


# In[20]:


def construct_hill_growth(input_file, country, backtesting):
    df = pd.read_csv(input_file, parse_dates=True)
    columns = df.columns.values
    for column in columns:
        if column == country:
            data = pd.DataFrame(df[column].values)
            
            data = data.reset_index(drop=False)
            data.columns = ['Timestep', 'Total Cases']
            
            # Randomly initialize the coefficients
            p0 = np.random.exponential(size=3)

            # Set min bound 0 on all coefficients, and set different max bounds for each coefficient
            coeff1 = 1000000.
            if country == 'USA_cases':
                coeff1 = 1000000000.
            if country == 'Brazil_cases':
                coeff1 = 1000000000.
            if country == 'Russia_cases':
                coeff1 = 1000000000.
            if country == 'India_cases':
                coeff1 = 1000000000.
            if country == 'France_cases':
                coeff1 = 1000000000.
            if country == 'Spain_cases':
                coeff1 = 1000000000.
            if country == 'UK_cases':
                coeff1 = 1000000000.
            if country == 'Italy_cases':
                coeff1 = 1000000000.
            if country == 'Argentina_cases':
                coeff1 = 1000000000.
            if country == 'Colombia_cases':
                coeff1 = 1000000000.
            if country == 'Mexico_cases':
                coeff1 = 1000000000.
            if country == 'Peru_cases':
                coeff1 = 1000000000.
            if country == 'Germany_cases':
                coeff1 = 1000000000.
            if country == 'Poland_cases':
                coeff1 = 1000000000.
            if country == 'Iran_cases':
                coeff1 = 1000000000.
            if country == 'South Africa_cases':
                coeff1 = 1000000000.
            if country == 'Ukraine_cases':
                coeff1 = 1000000000.
                
            bounds = (0, [coeff1, 100., 1000.])

            # Convert pd.Series to np.Array and use Scipy's curve fit to find the best Nonlinear Least Squares coefficients
            x = np.array(data['Timestep']) + 1
            y = np.array(data['Total Cases'])
            
            try:
                (a,b,c),cov = optim.curve_fit(func_hill, x, y, bounds=bounds, p0=p0, maxfev=1000)
                horizon = 21
                if backtesting == True:
                    horizon = 26
                for day in range(x[-1] + 1, x[-1] + horizon):
                    x = np.append(x, day)
                
                res_df = df[['Report_Date']].copy()
                future_range = pd.date_range(df['Report_Date'].iloc[-1], periods=horizon, freq='D')
                future_columns = {'Report_Date': future_range.strftime('%Y-%m-%d')}
                future_df = pd.DataFrame(future_columns)
                future_df = future_df.iloc[1:]
                res_df = res_df.append(future_df)

                res_df['y_hill'] = func_hill(x, a, b, c)
                res_df.columns = ['ds', 'y_hill']
                if backtesting == True:
                    res_df.columns = ['ds', 'y_hill_b1']
                
                return res_df
            except RuntimeError:
                print('-construct_hill_growth- No fit found for: ', column, backtesting)
            return None

# construct_hill_growth('data/covid19_data.csv', 'Brazil_cases', True)


# In[18]:


def build_model(country):
    try:
        df = pd.read_csv('data/covid19_processed_data_' + country + '.csv', parse_dates=True)
        forecast_b1 = None
        try:
            df_b1 = pd.read_csv('data/covid19_processed_backtesting_data_' + country + '.csv', parse_dates=True)
            df_b1 = df_b1[['Report_Date', country, 'cap']].dropna()
            df_b1.columns = ['ds', 'y', 'cap']
            m_b1 = Prophet(growth="logistic")
            m_b1.fit(df_b1)
            future_b1 = m_b1.make_future_dataframe(periods=25)
            future_b1['cap'] = df_b1['cap'].iloc[0]
            forecast_b1 = m_b1.predict(future_b1)
            forecast_b1 = forecast_b1[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].dropna()
            forecast_b1.columns = ['ds', 'yhat_b1', 'yhat_b1_lower', 'yhat_b1_upper']
        except FileNotFoundError:
            print('Skipping backtesing:', country)
            
        df_ = df.copy()
        df = df[['Report_Date', country, 'cap']].dropna()
        df.columns = ['ds', 'y', 'cap']

        m = Prophet(growth="logistic")
        m.fit(df)

        future = m.make_future_dataframe(periods=20)
        future['cap'] = df['cap'].iloc[0]
        forecast = m.predict(future)

        res_df = forecast.set_index('ds')[['yhat', 'yhat_lower', 'yhat_upper']].join(df.set_index('ds').y).reset_index()

        res_hill = construct_hill_growth('data/covid19_data.csv', country, False)
        if res_hill is not None:
            res_df = res_df.set_index('ds')[['yhat', 'yhat_lower', 'yhat_upper', 'y']].join(res_hill.set_index('ds')[['y_hill']]).reset_index()
        res_hill_b1 = construct_hill_growth('data/covid19_data_backtesting.csv', country, True)
        if res_hill_b1 is not None:
            res_df = res_df.set_index('ds')[['yhat', 'yhat_lower', 'yhat_upper', 'y', 'y_hill']].join(res_hill_b1.set_index('ds')[['y_hill_b1']]).reset_index()

        if forecast_b1 is not None and res_hill_b1 is not None:
            res_df = res_df.set_index('ds')[['yhat', 'yhat_lower', 'yhat_upper', 'y', 'y_hill', 'y_hill_b1']].join(forecast_b1.set_index('ds')[['yhat_b1', 'yhat_b1_lower', 'yhat_b1_upper']]).reset_index()
        
        res_df['current_date'] = df['ds'].iloc[-1]
        res_df['active_patients'] = df_['active_patients']
        res_df['fastest_growth_day'] = df_['fastest_grow_day'].iloc[-1]
        res_df['growth_stabilized'] = df_['growth_stabilized'].iloc[-1]
        res_df['current_day'] = df_['timestep'].iloc[-1]
        res_df['cap'] = df['cap'].iloc[0]

        res_df.to_csv('data/covid19_forecast_data_' + country + '.csv')

        print('Processed:', country)
    except FileNotFoundError:
        print('Skipping:', country)
    
#     fig1 = m.plot(forecast)
#     fig1.set_size_inches(18.5, 8.5)
#     datenow = datetime(2020, 4, 5)
#     dateend = datenow + timedelta(days=20)
#     datestart = dateend - timedelta(days=71)
#     plt.xlim([datestart, dateend])
#     plt.title("COVID19 forecast: " + country, fontsize=20)
#     plt.xlabel("Day", fontsize=20)
#     plt.ylabel("Infections", fontsize=20)
#     plt.axvline(datenow, color="k", linestyle=":")
#     plt.show()
    
#     print(res_df[['ds', 'y', 'yhat', 'yhat_lower', 'yhat_upper', 'current_date', 'fastest_growth_day', 'growth_stabilized', 'current_day']].tail(30))
    
# build_model('Brazil_cases')


# In[19]:


def calculate_forecast():
    df = pd.read_csv('data/covid19_data.csv', parse_dates=True)
    columns = df.columns.values
    for column in columns:
        if column.endswith('_cases'):
            build_model(column)
    print('Forecast calculation completed')
    
# calculate_forecast()

