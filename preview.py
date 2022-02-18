from os import path
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from flask import Flask
from jinja2 import Environment, FileSystemLoader
import requests

app = Flask(__name__)

# Jinja2 environment.
root = path.dirname(path.abspath(__file__))
env = Environment(loader=FileSystemLoader(path.join(root, "templates")))


TEST_URLS = [
    # YouTube.
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    # Twitter with image.
    "https://twitter.com/matrixdotorg/status/1492207278560268289",
    # Twitter with link.
    "https://twitter.com/matrixdotorg/status/1493535149899849735",
    # Reply / no media.
    "https://twitter.com/matrixdotorg/status/1492211991624224770",
    # Twitter moments.
    "https://twitter.com/cnn/moments",
    "https://twitter.com/i/events/1203845439952429057",
    # GIFs.
    "https://tenor.com/view/pedro-monkey-puppet-meme-awkward-gif-15268759",
    "https://imgur.com/t/science_and_tech/RDcElS2",
    "https://imgur.com/t/science_and_tech/ZhioqHP",
    # Reddit
    "https://www.reddit.com/r/matrixdotorg/",
    # Reddit with link.
    "https://www.reddit.com/r/matrixdotorg/comments/snkooa/how_fosdem_2022_was_hosted_on_matrix/",
    # Reddit with image.
    "https://www.reddit.com/r/matrixdotorg/comments/rsh7gb/working_on_a_python_matrix_bot_bot_library/",
    # Reddit without anything.
    "https://www.reddit.com/r/matrixdotorg/comments/s5m47u/cant_connect_to_my_home_server_in_element/",
    # Flickr
    "https://www.flickr.com/photos/roland/51382873958/",
    # GitHub
    "https://github.com/matrix-org/synapse",
    "https://github.com/matrix-org/synapse/issues/11563",
    "https://github.com/matrix-org/synapse/pull/11669",
    # "http://www.bibliotecapleyades.net/tierra_hueca/esp_tierra_hueca_2d.ht",
    # "https://www.bibliotecapleyades.net/tierra_hueca/esp_tierra_hueca_2d.htm",
    # "ftp://ftp.ics.uci.edu/README",
    # "ftp://ftp.ics.uci.edu/READMEA",
    # "data:,Hello, World!",
    # "data:,HelloWorld",
    # "data:text/html,<h1>Hello, World!</h1>",
    # "https://radio.anarc.at/radio.mp3",
    # "https://24413.live.streamtheworld.com/WERSFM_SC",
]

HOMESERVER = "http://localhost:8080"
ACCESS_TOKEN = "syt_dGVzdGVy_TTcACJuKenrxfVIKsNaJ_0kYC9a"


def get_version(homeserver):
    req = requests.get(f"{homeserver}/_matrix/federation/v1/version")
    result = req.json()
    return result["server"]["version"]


def preview_url(homeserver, access_token, url, extra):
    parsed_url = urlparse(url)
    parameters = parse_qs(parsed_url.query)
    parameters.update(extra)
    url = urlunparse((*parsed_url[0:4], urlencode(parameters, doseq=True), parsed_url[5]))

    req = requests.get(
        f"{homeserver}/_matrix/media/r0/preview_url",
        params={"url": url, **extra},
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=60,
    )

    # Replace any mxc:// URL with something reasonable.
    result = req.json()
    for key, value in result.items():
        if isinstance(value, str) and value.startswith("mxc://"):
            result[key] = f"{homeserver}/_matrix/media/v3/thumbnail/{value[6:]}?height=96&width=96"

    return result


@app.route("/")
def root():
    # Get the server version.
    version = get_version(HOMESERVER)

    results = [preview_url(HOMESERVER, ACCESS_TOKEN, url, {"cache_buster": version}) for url in TEST_URLS]

    template = env.get_template("base.html")
    return template.render(homeserver=HOMESERVER, version=version, results=results)


if __name__ == "__main__":
    # This is only used for development purposes, run `python server.py`.
    app.run(debug=True)
