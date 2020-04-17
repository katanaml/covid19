
# coding: utf-8

# In[1]:


import covid19_model as model


# In[ ]:


def run_training():
    model.fetch_data()
    model.detect_growth('data/covid19_data.csv', 'data/covid19_processed_data_', False)
    model.detect_growth('data/covid19_data_backtesting.csv', 'data/covid19_processed_backtesting_data_', True)
    model.calculate_forecast()
    
run_training()

