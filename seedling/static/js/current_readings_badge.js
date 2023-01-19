function updateBadge(data) {
    "use strict";
  let container = document.getElementById("climate-badge-reading");
  container.innerHTML = `${data.degrees_fahrenheit}°F/${data.percent_humidity}%`
}


function loadCurrentReadingData(currentReadingURL) {
    "use strict";
    jQuery.getJSON(currentReadingURL, updateBadge);
    setInterval(() => jQuery.getJSON(currentReadingURL, updateBadge), 1000 * 60)
}
