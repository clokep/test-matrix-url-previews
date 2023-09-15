import json
import os
import sys

import requests


TEST_URLS = {
    "YouTube": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "YouTube Shorts": "https://www.youtube.com/shorts/usofnFoFNN4",
    "Twitter with link": "https://twitter.com/matrixdotorg/status/1493535149899849735",
    "Twitter with image": "https://twitter.com/matrixdotorg/status/1492207278560268289",
    "Twitter reply": "https://twitter.com/matrixdotorg/status/1492211991624224770",
    "Twitter moments": "https://twitter.com/i/events/1203845439952429057",
    "Tenor gif": "https://tenor.com/view/pedro-monkey-puppet-meme-awkward-gif-15268759",
    "imgur gif": "https://imgur.com/t/science_and_tech/RDcElS2",
    "imgur video": "https://imgur.com/t/science_and_tech/ZhioqHP",
    "Reddit": "https://www.reddit.com/r/matrixdotorg/",
    "Reddit post": "https://www.reddit.com/r/matrixdotorg/comments/s5m47u/cant_connect_to_my_home_server_in_element/",
    "Reddit post with link": "https://www.reddit.com/r/matrixdotorg/comments/snkooa/how_fosdem_2022_was_hosted_on_matrix/",
    "Reddit post with image": "https://www.reddit.com/r/matrixdotorg/comments/rsh7gb/working_on_a_python_matrix_bot_bot_library/",
    "Flickr": "https://www.flickr.com/photos/roland/51382873958/",
    "GitHub repo": "https://github.com/matrix-org/synapse",
    "Github issue": "https://github.com/matrix-org/synapse/issues/11563",
    "GitHub PR": "https://github.com/matrix-org/synapse/pull/11669",
    "Twitter card metadata-only": "https://lwn.net/Articles/897712/",
}

def get_version(homeserver: str) -> str:
    req = requests.get(f"{homeserver}/_matrix/federation/v1/version")
    result = req.json()
    return result["server"]["version"]


def preview_url(homeserver: str, access_token: str, directory: str, url: str) -> None:
    req = requests.get(
        f"{homeserver}/_matrix/media/r0/preview_url",
        params={"url": url},
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=60,
    )

    # Replace any mxc:// URL with something reasonable.
    result = req.json()
    if "og:image" in result:
        full_mxc = result["og:image"][6:]
        mxc = full_mxc.split("/")[1]
        ext = result["og:image:type"].split("/")[1]
        with open(directory + "/" + mxc  + "." + ext, "wb") as f:
            req = requests.get(f"{homeserver}/_matrix/media/r0/download/{full_mxc}")
            f.write(req.content)
        with open(directory + "/" + mxc + ".sm." + ext, "wb") as f:
            req = requests.get(f"{homeserver}/_matrix/media/r0/thumbnail/{full_mxc}?height=200&width=200")
            f.write(req.content)

    return result


def main(homeserver: str, access_token: str) -> None:
    version = get_version(homeserver)

    directory = "v" + version
    os.makedirs(directory)

    # TODO Include the date and the date of the image.
    results = {
        "version": version,
        "queries": [],
    }
    for desc, url in TEST_URLS.items():
        result = preview_url(homeserver, access_token, directory, url)
        results["queries"].append({
            "description": desc,
            "url": url,
            "result": result,
        })

    with open(directory + "/results.json", "w") as f:
        json.dump(results, f)


if __name__ == "__main__":
    _, homeserver, access_token = sys.argv
    main(homeserver, access_token)
