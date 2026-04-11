import os
from pathlib import Path
from typing import TypedDict


class Entry(TypedDict):
    name: str
    absolute: str
    file: bool


def dir_entries(path: str) -> tuple[list[Entry], str]:
    """Returns a tuple with the list of dir entries, and its parent"""
    filter = {".", ".."}

    files = []
    for f in os.listdir(path):
        if f in filter:
            continue

        full = os.path.join(path, f)

        if f.startswith("."):
            continue

        if os.path.isfile(full) or os.path.isdir(full):
            files.append(Entry(name=f, absolute=full, file=os.path.isfile(full)))

    files.sort(key=lambda f: f["name"])
    prev = str(Path(path).parent)

    return files, prev
