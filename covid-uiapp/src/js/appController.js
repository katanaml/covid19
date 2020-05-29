/**
 * @license
 * Copyright (c) 2014, 2019, Oracle and/or its affiliates.
 * The Universal Permissive License (UPL), Version 1.0
 */
/*
 * Your application specific code will go here
 */
define(['ojs/ojresponsiveutils', 'ojs/ojresponsiveknockoututils', 'knockout', 'ojs/ojarraydataprovider', 'ojs/ojconverter-datetime',
  'ojs/ojknockout', 'ojs/ojchart', 'ojs/ojselectcombobox', 'ojs/ojgauge'],
  function (ResponsiveUtils, ResponsiveKnockoutUtils, ko, ArrayDataProvider, DateTimeConverter) {
    function ControllerViewModel() {
      var self = this;
      // let baseURL = 'https://app.katanaml.io/katana-ml/api/v1.0/forecast/covid19';
      let baseURL = 'http://127.0.0.1:3000/katana-ml/api/v1.0/forecast/covid19';

      let dateConverter = new DateTimeConverter.IntlDateTimeConverter(
        {
          pattern: 'dd/MM/yyyy'
        });
      self.headerTitle = ko.observable('CURRENT SITUATION');
      self.lastAvailableDate = ko.observable();

      self.covidSummary = ko.observableArray();
      self.dataProviderSummary = new ArrayDataProvider(self.covidSummary, { keyAttributes: 'id' });

      self.currentCountry = ko.observable();
      self.countriesList = ko.observableArray();
      self.dataProviderCountries = new ArrayDataProvider(self.countriesList, { keyAttributes: 'value' });
      self.thresholdValue = ko.observable();
      self.colorGauge = ko.observable();

      self.covid19Forecast = ko.observableArray();
      self.covid19ForecastDataProvider = new ArrayDataProvider(self.covid19Forecast, { keyAttributes: 'id' });
      self.xAxisData = ko.observable();
      self.yAxisDataForecast = ko.observable();

      self.currentCountry.subscribe(function (newValue) {
        self.fetchStatsPerCountry(newValue);
      });

      self.fetchAllStats = function () {
        let fetchURL = baseURL + '/stats';
        fetch(fetchURL, {
          method: 'get',
          headers: {
            "Content-type": "application/json"
          }
        }).then(function (response) {
          if (response.status !== 200) {
            console.log('Looks like there was a problem. Status Code: ' + response.status);
            return;
          }

          response.json().then(function (data) {
            self.covidSummary.removeAll();
            self.covidSummary.push({ "id": 1, "series": "Countries COVID-19 Stabilized", "group": "Countries total: " + data[0].countries_processed, "value": data[0].countries_stabilized });
            self.covidSummary.push({ "id": 2, "series": "Countries COVID-19 Increasing", "group": "Countries total: " + data[0].countries_processed, "value": data[0].countries_increasing });
          });
        })
      }
      self.fetchAllStats();

      self.fetchAllCountries = function () {
        let fetchURL = baseURL + '/countries';
        fetch(fetchURL, {
          method: 'get',
          headers: {
            "Content-type": "application/json"
          }
        }).then(function (response) {
          if (response.status !== 200) {
            console.log('Looks like there was a problem. Status Code: ' + response.status);
            return;
          }

          response.json().then(function (data) {
            self.countriesList.removeAll();
            data.forEach(function (item) {
              self.countriesList.push({ value: item[0], label: item[0].replace("_cases", "") });
            })
            self.currentCountry('Lithuania_cases');
          })
        })
      }
      self.fetchAllCountries();

      self.fetchStatsPerCountry = function (country) {
        let fetchURL = baseURL;
        fetch(fetchURL, {
          method: 'post',
          headers: {
            "Content-type": "application/json"
          },
          body: '{'
            + '"country": ' + '"' + country + '"' +
            '}'
        }).then(function (response) {
          if (response.status !== 200) {
            console.log('Looks like there was a problem. Status Code: ' + response.status);
            return;
          }

          response.json().then(function (data) {
            let itemsRangeForecastProphet = [];
            let itemsRangeForecastProphetBacktest = [];
            let fastestGrowthDay = Math.round(data[0].fastest_growth_day);
            let fastestGrowthDate = null;
            self.lastAvailableDate(dateConverter.format(data[0].current_date));
            self.headerTitle('CURRENT SITUATION - ' + self.lastAvailableDate());
            let expectedTop = data[0].cap;
            if (data[0].growth_stabilized === true) {
              self.thresholdValue(70);
              self.colorGauge('#e7b416');
            } else {
              self.thresholdValue(30);
              self.colorGauge('#cc3232');
            }

            self.covid19Forecast.removeAll();
            let idCovid19 = 0;

            if (fastestGrowthDay < data.length) {
              fastestGrowthDate = data[fastestGrowthDay - 1].ds;
            }
            lastDate = new Date(data[0].current_date);

            if (fastestGrowthDate === null) {
              let constantLineX = {
                referenceObjects: [
                  { text: 'Last Available Day', type: 'line', value: lastDate, color: '#000000', displayInLegend: 'on', lineWidth: 1, location: 'back', lineStyle: 'dashed', shortDesc: 'Last Available Day' }
                ]
              };
              self.xAxisData(constantLineX);
            } else {
              fastestGrowthDate = new Date(fastestGrowthDate);
              let constantLineX = {
                referenceObjects: [
                  { text: 'Last Available Day', type: 'line', value: lastDate, color: '#000000', displayInLegend: 'on', lineWidth: 2, location: 'back', lineStyle: 'dashed', shortDesc: 'Last Available Day' },
                  { text: 'Fastest Growth Day', type: 'line', value: fastestGrowthDate, color: '#cc3232', displayInLegend: 'on', lineWidth: 2, location: 'back', lineStyle: 'line', shortDesc: 'Fastest Growth Day' }
                ]
              };
              self.xAxisData(constantLineX);
            }

            data.forEach(function (item) {
              if (item.y > 0 || item.y === null) {
                self.covid19Forecast.push({ "id": idCovid19, "date": item.ds, "series": "Forecast Logistic", "value": item.yhat });
                idCovid19 = idCovid19 + 1;
                self.covid19Forecast.push({ "id": idCovid19, "date": item.ds, "series": "Forecast Logistic Backtest", "value": item.yhat_b1 });
                idCovid19 = idCovid19 + 1;
                self.covid19Forecast.push({ "id": idCovid19, "date": item.ds, "series": "Forecast Hill", "value": item.y_hill });
                idCovid19 = idCovid19 + 1;
                self.covid19Forecast.push({ "id": idCovid19, "date": item.ds, "series": "Forecast Hill Backtest", "value": item.y_hill_b1 });
                idCovid19 = idCovid19 + 1;
                self.covid19Forecast.push({ "id": idCovid19, "date": item.ds, "series": "Actual Infections", "value": item.y });
                idCovid19 = idCovid19 + 1;
                self.covid19Forecast.push({ "id": idCovid19, "date": item.ds, "series": "Active Patients", "value": item.active_patients });
                idCovid19 = idCovid19 + 1;
                itemsRangeForecastProphet.push({ low: item.yhat_lower, high: item.yhat_upper });
                itemsRangeForecastProphetBacktest.push({ low: item.yhat_b1_lower, high: item.yhat_b1_upper });
              }
            });

            var variedAreaForecastY = {
              baselineScaling: 'min',
              referenceObjects: [{
                text: 'Forecast Range', type: 'area', items: itemsRangeForecastProphet, color: '#f7e4d4', displayInLegend: 'on', location: 'back', shortDesc: 'Forecast Range'
              },
              {
                text: 'Forecast Range Backtest', type: 'area', items: itemsRangeForecastProphetBacktest, color: '#f7e4d4', displayInLegend: 'on', location: 'back', shortDesc: 'Forecast Range Backtest'
              },
              {
                text: 'Expected Maximum', type: 'line', value: expectedTop, color: '#000000', displayInLegend: 'on', lineWidth: 1, location: 'back', lineStyle: 'dashed', shortDesc: 'Expected Maximum'
              }]
            };
            self.yAxisDataForecast(variedAreaForecastY);

          })
        }).catch(function (err) {
          console.log('Fetch Error :-S', err);
        })
      }
      self.fetchStatsPerCountry('Lithuania_cases');

      // Footer
      function footerLink(name, id, linkTarget) {
        this.name = name;
        this.linkId = id;
        this.linkTarget = linkTarget;
      }
      self.footerLinks = ko.observableArray([
        new footerLink('About Katana ML', 'aboutKatana', 'https://katanaml.io/'),
        new footerLink('GitHub', 'github', 'https://github.com/katanaml/covid19'),
        new footerLink('NovelCOVID API', 'dataAPI', 'https://github.com/novelcovid/api')
      ]);
    }

    return new ControllerViewModel();
  }
);
