import hashlib
from io import BytesIO
from pathlib import Path
import sys
import zipfile
import requests

# version: https://github.com/jasmine/jasmine/releases/tag/v6.3.0
JASMINE_STANDALONE_URL = "https://github.com/jasmine/jasmine/releases/download/v6.3.0/jasmine-standalone-6.3.0.zip"
JASMINE_HASH = "805bc0ad270caea4c867af74ec4ac973db141a443bcc98b888ac47f374807d3a"
JASMINE_LIB_PATH = Path("tests", "lib")

if __name__ == "__main__":
    if JASMINE_LIB_PATH.exists():
        exit()

    response = requests.get(JASMINE_STANDALONE_URL, timeout=5)
    response.raise_for_status()
    content = response.content
    if hashlib.sha256(content).hexdigest() != JASMINE_HASH:
        print("Jasmine binary does not match hash", file=sys.stderr)
        exit(1)

    with zipfile.ZipFile(BytesIO(content), "r") as zip:
        for file in zip.filelist:
            if file.filename.startswith("lib"):
                zip.extract(file, "tests")
