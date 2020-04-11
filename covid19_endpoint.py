
# coding: utf-8

# In[1]:


import subprocess
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit

from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import pandas as pd
import numpy as np

import covid19_model as model


# In[2]:


access_count = 0

def run_training():
    model.fetch_data()
    model.detect_growth('data/covid19_data.csv', 'data/covid19_processed_data_', False)
    model.detect_growth('data/covid19_data_backtesting.csv', 'data/covid19_processed_backtesting_data_', True)
    model.calculate_forecast()
    
scheduler = BackgroundScheduler()
scheduler.start()

scheduler.add_job(
    func=run_training,
    trigger='cron',
    hour='2', 
    minute='00')

atexit.register(lambda: scheduler.shutdown())


# In[3]:


app = Flask(__name__)
CORS(app)

@app.route("/katana-ml/api/v1.0/forecast/covid19", methods=['POST'])
def forecast():
    global access_count
    access_count += 1
    
    country = request.json['country']
    
    df = pd.read_csv('data/covid19_forecast_data_' + country + '.csv', parse_dates=True)
    df = df.drop(df.columns[[0]], axis=1)
    
    result = df.to_json(orient='records', date_format='iso')
    return result

@app.route("/katana-ml/api/v1.0/forecast/covid19/stats", methods=['GET'])
def stats():
    df = pd.read_csv('data/covid19_stats_countries.csv', parse_dates=True)
    df = df.drop(df.columns[[0]], axis=1)
    
    result = df.to_json(orient='records', date_format='iso')
    return result

@app.route("/katana-ml/api/v1.0/forecast/covid19/count", methods=['GET'])
def accecc_count():
    global access_count
    return str(access_count)

@app.route("/katana-ml/api/v1.0/forecast/covid19/countries", methods=['GET'])
def get_countries():
    df = pd.read_csv('data/covid19_countries_list.csv')
    df = df.drop(df.columns[[0]], axis=1)
    
    result = df.to_json(orient='records', date_format='iso')
    return result

# running REST interface port=5001
if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5001)

