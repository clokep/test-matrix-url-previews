const testUrls = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "http://www.bibliotecapleyades.net/tierra_hueca/esp_tierra_hueca_2d.ht",
    "https://www.bibliotecapleyades.net/tierra_hueca/esp_tierra_hueca_2d.htm",
    "ftp://ftp.ics.uci.edu/README",
    "ftp://ftp.ics.uci.edu/READMEA",
    "data:,Hello, World!",
    "data:,HelloWorld",
    "data:text/html,<h1>Hello, World!</h1>",
    "https://radio.anarc.at/radio.mp3",
    "https://24413.live.streamtheworld.com/WERSFM_SC",
]

function start() {
    const homeserver = document.getElementById("homeserver").value + "/_matrix/media/r0/preview_url";
    const accessToken = document.getElementById("access-token").value;

    previewUrl(homeserver, accessToken, testUrls[0]);
}

function previewUrl(homeserver, accessToken, url) {
    const results = document.getElementById("results");
    const result = document.createElement("div");
    results.innerText = "Pending . . .";
    results.appendChild(result);

    fetch(homeserver + "?url=" + encodeURIComponent(url), {
        headers: {
            "Authorization": `Bearer ${accessToken}`,
        },
        "credentials": "same-origin",
    }).then(function(response) {
        console.log("GOT RESPONSE");
        if (!response.ok) {
            // for non-200 responses, raise the body of the response as an exception
            return response.text().then((text) => { throw new Error(text); });
        } else {
            return response.json();
        }
    }).then(function(json) {
        console.log(json);
        renderResult(json, result);
    });
}

function renderResult(openGraph, element) {
    console.log("HERE")
}
