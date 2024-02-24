function runContinuousImageRefresh(latestImageURL, intervalSecs) {
    const interval = setInterval(() => {loadLatestImageData(latestImageURL)}, intervalSecs * 5000);
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
  let caption = document.getElementById("image-age");

  if (currentId == data.id) {
    caption.textContent =  `Image taken ${data.age}`
    console.log("Nothing has changed.")
    return;

  }
  image.src = data.url;
  image.dataset.imageId = currentId;
  caption.textContent =  `Image taken ${data.age}`

}
