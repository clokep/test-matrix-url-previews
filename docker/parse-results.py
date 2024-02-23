import json
import sys
from collections import defaultdict

def parse(path: str) -> None:
    with open(path + "/results.json", "r") as f:
        data = json.load(f)

    with open(path + "/created", "r") as f:
        created = f.read().strip()

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
        title = query["result"].get("og:title")

        # If the site returned an error or says that JavaScript is required.
        if "errcode" in query["result"]:
            error += 1
        elif title is not None and "JavaScript" in title:
            javascript += 1
        else:
            success += 1

            if "og:image" in query["result"]:
                image += 1
            if "og:description" in query["result"]:
                description += 1

    print(data["version"])
    print(f"Created: {created}, queried: {data['date']}")
    print(f"Success: {success} / {total} (errors: {error}, javascript req: {javascript})")
    print(f"Image: {image} / {total}")
    print(f"Description: {image} / {total}")
    print()


if __name__ == "__main__":
    versions = sys.argv[1:]
    for version in versions:
        parse(version)
