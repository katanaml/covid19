
# coding: utf-8

# In[1]:


from apscheduler.schedulers.blocking import BlockingScheduler
import sys

import covid19_model as model


# In[2]:


def run_training():
    model.fetch_data()
    model.detect_growth('data/covid19_data.csv', 'data/covid19_processed_data_', False)
    model.detect_growth('data/covid19_data_backtesting.csv', 'data/covid19_processed_backtesting_data_', True)
    model.calculate_forecast()
    
scheduler = BlockingScheduler()
scheduler.add_job(
    func=run_training,
    trigger='cron',
    hour='1', 
    minute='00')
scheduler.start()

atexit.register(lambda: scheduler.shutdown())

