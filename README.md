# covid19
COVID-19 Growth Forecast

Web UI (data is updated daily): https://app.katanaml.io/covid19/

Article I: https://medium.com/katanaml/covid-19-growth-modeling-and-forecasting-with-prophet-2ff5ebd00c01

Article II: https://medium.com/katanaml/covid-19-growth-modeling-forecasting-with-logistic-hill-equations-and-prophet-8b9937152f5

Technology: Python, Prophet

Author: Katana, Red Samurai Consulting, Andrej Baranovskij

## Instructions

See covid19_endpoint.py, function run_training is responsible to execute re-training

## API

curl --data "country=Lithuania_cases" https://app.katanaml.io/katana-ml/api/v1.0/forecast/covid19

curl https://app.katanaml.io/katana-ml/api/v1.0/forecast/covid19/countries

curl https://app.katanaml.io/katana-ml/api/v1.0/forecast/covid19/stats

## License

Licensed under the Apache License, Version 2.0. Copyright 2020 Katana ML. [Copy of the license](https://github.com/katanaml/covid19/blob/master/LICENSE).
