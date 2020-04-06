# covid19
COVID-19 Growth Forecast

Web UI: https://app.katanaml.io/covid19/

Technology: Python, Prophet

Author: Katana, Red Samurai Consulting, Andrej Baranovskij

## Instructions

Fetch latest data: run fetch_data() function from covid19_model.ipynb

Detect growth rates for all countries: run detect_growth() function from covid19_model.ipynb

Execute forecast per country: run build_model() function from covid19_model.ipynb

## API

curl --data "country=Lithuania_cases" https://app.katanaml.io/katana-ml/api/v1.0/forecast/covid19

curl https://app.katanaml.io/katana-ml/api/v1.0/forecast/covid19/countries

## License

Licensed under the Apache License, Version 2.0. Copyright 2019 Red Samurai Consulting. [Copy of the license](https://github.com/katanaml/covid19/blob/master/LICENSE).
