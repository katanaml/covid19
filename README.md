# covid19
COVID-19 Growth Forecast

Web UI (data is updated daily): https://app.katanaml.io/covid19/

Article: https://medium.com/katanaml/covid-19-growth-modeling-and-forecasting-with-prophet-2ff5ebd00c01

Technology: Python, Prophet

Author: Katana, Red Samurai Consulting, Andrej Baranovskij

## Instructions

See covid19_endpoint.py, function run_training is responsible to execute re-training

## API

curl --data "country=Lithuania_cases" https://app.katanaml.io/katana-ml/api/v1.0/forecast/covid19

curl https://app.katanaml.io/katana-ml/api/v1.0/forecast/covid19/countries

curl https://app.katanaml.io/katana-ml/api/v1.0/forecast/covid19/stats

## License

Licensed under the Apache License, Version 2.0. Copyright 2019 Red Samurai Consulting. [Copy of the license](https://github.com/katanaml/covid19/blob/master/LICENSE).
