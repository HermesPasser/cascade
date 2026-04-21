from itertools import chain
import os
from pathlib import Path
import tempfile
from typing import Protocol, Sequence, TypedDict

from unzip import get_first_file

SUPPORTED_IMAGE_EXTENSIONS = ("png", "jpeg", "jpg", "gif", "webp")
SUPPORTED_ARCHIVE_EXTENSIONS = {"zip", "cbz", "epub"}


class Entry(TypedDict):
    name: str
    absolute: str
    file: bool
    thumbnail: str


def dir_entries(
    path: str, extensions: set[str] = SUPPORTED_ARCHIVE_EXTENSIONS
) -> tuple[list[Entry], str]:
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
        is_file = os.path.isfile(full)
        if is_file and not any(f.endswith(f".{e}") for e in extensions):
            continue

        if is_file or os.path.isdir(full):
            thumb = _get_thumbnail(full)
            files.append(Entry(name=f, absolute=full, file=is_file, thumbnail=thumb))

    files.sort(key=lambda f: f["name"])
    prev = str(Path(path).parent)

    return files, prev


def _get_thumbnail(
    filename: str,
):
    """This get the first image in the path that we find, not the _fist_ image"""
    full = Path(filename)
    filter_fn = lambda file: any(
        file.lower().endswith(e) for e in SUPPORTED_IMAGE_EXTENSIONS
    )

    # If the path is a file, then the file is an archive. Get the first image form it
    if full.is_file():
        return get_first_file(full, filter_fn) or ""

    try:
        # If is not an archive, then is a folder. Get the first image we can find from that folder
        return str(next(iterate_images(full)))
    except StopIteration:
        pass

    try:
        # If the folder has no images, look for the first archive we found in that
        # folder and search for the first image in it
        archive_path = next(iterate_archives(full))
        return get_first_file(archive_path, filter_fn) or ""
    except StopIteration:
        pass

    return ""


def iterate_archives(path: Path):
    return chain(
        *(
            path.glob(f"**/*.{pat}", case_sensitive=False)
            for pat in SUPPORTED_ARCHIVE_EXTENSIONS
        )
    )


def iterate_images(path: Path):
    return chain(
        *(
            path.glob(f"**/*.{pat}", case_sensitive=False)
            for pat in SUPPORTED_IMAGE_EXTENSIONS
        )
    )


def list_images_from_folder(folder: str):
    path = Path(folder)
    if not path.is_dir():
        raise ValueError("Path is not a folder")

    it = iterate_images(path)
    images = [str(file) for file in it]
    images.sort()
    return images


class Savable(Protocol):
    @property
    def filename(self) -> str | None: ...
    def save(self, dst: os.PathLike[str]): ...


def save_to_temp_folder(files: Sequence[Savable]):
    directory = Path(tempfile.mkdtemp())
    size = len(files)

    for i, file in enumerate(files, start=1):
        name = str(i).zfill(len(str(size)))
        name += "-" + file.filename if file.filename else ""
        file.save(directory / name)

    return str(directory)
