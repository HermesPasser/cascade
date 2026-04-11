from itertools import chain
import os
from pathlib import Path
from typing import TypedDict


class Entry(TypedDict):
    name: str
    absolute: str
    file: bool


def dir_entries(path: str, extensions: set[str]) -> tuple[list[Entry], str]:
    """
    Returns a tuple with the list of non-hidden dir entries, and its parent.
    All files that not end with extensions in extensions param are ignored.
    """
    filter = {".", ".."}
    files = []

    for f in os.listdir(path):
        if f in filter or f.startswith("."):
            continue

        full = os.path.join(path, f)
        if os.path.isfile(full) and not any(f.endswith(e) for e in extensions):
            continue

        if os.path.isfile(full) or os.path.isdir(full):
            files.append(Entry(name=f, absolute=full, file=os.path.isfile(full)))

    files.sort(key=lambda f: f["name"])
    prev = str(Path(path).parent)

    return files, prev


SUPPORTED_FILE_EXTENSIONS = ["png", "jpeg", "jpg", "gif", "webp"]


def list_images_from_folder(folder: str):
    path = Path(folder)
    if not path.is_dir():
        raise ValueError("Path is not a folder")

    it = chain(
        *(
            path.glob(f"**/*.{pat}", case_sensitive=False)
            for pat in SUPPORTED_FILE_EXTENSIONS
        )
    )

    images = [str(file) for file in it]
    images.sort()
    return images
