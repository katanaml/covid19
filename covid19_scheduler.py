
# coding: utf-8

# In[1]:


import subprocess
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit
import sys

import covid19_model as model


# In[ ]:


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
    hour='1', 
    minute='00')

atexit.register(lambda: scheduler.shutdown())

immediate_run = sys.argv[1]
if immediate_run == 'true':
    run_training()

