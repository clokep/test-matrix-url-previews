import json
import sys
from collections import defaultdict

def parse(filename: str) -> None:
    with open(filename, "r") as f:
        data = json.load(f)

    # Overall status.
    error = 0
    success = 0
    javascript = 0
    total = len(data["queries"])

    # Whether an image was found.
    image = 0

    # Whether a description was found.
    description = 0

    for query in data["queries"]:
        # If the site returned an error or says that JavaScript is required.
        if "errcode" in query["result"]:
            error += 1
        elif "JavaScript" in query["result"]["og:title"]:
            javascript += 1
        else:
            success += 1

            if "og:image" in query["result"]:
                image += 1
            if "og:description" in query["result"]:
                description += 1

    print(f"Success: {success} / {total} (errors: {error}, javascript req: {javascript})")
    print(f"Image: {image} / {total}")
    print(f"Description: {image} / {total}")


if __name__ == "__main__":
    _, version = sys.argv
    parse("v" + version + "/results.json")
