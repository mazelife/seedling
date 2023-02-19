function renderCharts(sourceData, dateRangeLabel) {

    document.getElementById("daterange-submit").classList.add("visually-hidden");

    const layout = {paper_bgcolor: "#6d7782"}
    const rangePicker = document.getElementById("daterange-select");
    const rangeForm = document.getElementById("daterange-form");

    const tempData = [
      {
        x: sourceData.map((el) => el.created),
        y: sourceData.map((el) => el.degrees_fahrenheit),
        type: "scatter",
        line: {
          color: "rgb(234, 139, 44)"
        }
      }
    ];
    Plotly.newPlot('temperature-chart', tempData, {title: `Temperature (${dateRangeLabel})`, yaxis: {title: "°F"}});

    const humidityData = [
      {
        x: sourceData.map((el) => el.created),
        y: sourceData.map((el) => el.percent_humidity),
        type: "scatter",
        line: {
          color: "rgb(44, 182, 234)"
        }

      }
    ]
    Plotly.newPlot('humidity-chart', humidityData, {title: `Humidity (${dateRangeLabel})`, yaxis: {title: "% Humidity"}});

    rangePicker.addEventListener("change", (evt) => {
        rangeForm.submit()
    });

}
