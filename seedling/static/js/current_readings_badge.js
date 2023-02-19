function handleResponse(response) {
    "use strict";
    if (response.ok) {
        return response.json();
    } else {
        throw new Error(`Error in getting temperature reading (response code ${response.code})`);
    }
}

function updateBadge(data) {
    "use strict";
  let container = document.getElementById("climate-badge-reading");
  let badge = document.getElementById("climate-badge");
  if (data.degrees_fahrenheit < 36) {
    badge.classList.add("danger");
  } else {
    badge.classList.remove("danger");
  }
  container.innerHTML = `${data.degrees_fahrenheit}°F/${data.percent_humidity}%`
}


function loadCurrentReadingData(currentReadingURL) {
    "use strict";
    fetch(currentReadingURL).then(handleResponse).then(updateBadge).catch(window.alert);

}

function initializeBadge(currentReadingURL) {
    "use strict";
    loadCurrentReadingData(currentReadingURL);
    setInterval(() => loadCurrentReadingData(currentReadingURL), 1000 * 60)
}
