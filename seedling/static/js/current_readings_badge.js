function loadCurrentReadingData(currentReadingURL) {
    "use strict";
    jQuery.getJSON(currentReadingURL, (data) => {
      let container = document.getElementById("climate-badge-reading");
      container.innerHTML = `${data.degrees_fahrenheit}°F/${data.percent_humidity}%`
    });
}
