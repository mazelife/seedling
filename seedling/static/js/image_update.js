function runContinuousImageRefresh(latestImageURL, intervalSecs) {
    const interval = setInterval(() => {loadLatestImageData(latestImageURL)}, intervalSecs * 1000);
}


function loadLatestImageData(latestImageURL) {
    "use strict";
    fetch(latestImageURL).then(handleResponse).then(updateImage).catch(window.alert);
}


function handleResponse(response) {
    "use strict";
    if (response.ok) {
        return response.json();
    } else {
        throw new Error(`Error in getting latest image data (response code ${response.code})`);
    }
}


function updateImage(data) {
    "use strict";
  if (!data.url || ! data.id) {
    return;
  }

  let image = document.getElementById("current-image");
  let currentId = Number(image.dataset.imageId);

  if (currentId == data.id) {
    console.log("Nothing has changed.")
    return;

  }
  image.src = data.url;
  image.dataset.imageId = currentId;
  document.getElementById("image-age").textContent =  `Image taken ${data.age}`

}
