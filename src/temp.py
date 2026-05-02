from collections.abc import Sequence
from hashlib import sha1
from os import PathLike
from pathlib import Path
from tempfile import gettempdir, mkdtemp
from typing import Protocol

_TEMP_DIR = Path(gettempdir(), "cascade")


def temp_name_for(path: str | PathLike) -> Path:
    """
    Saves a file in a custom folder in the system temporary folder.
    The same 'path' is guarantee to always have the same name.

    This is usefull for needing to store the file into the temp folder
    multiple times without worring about ending making multiple copies.
    """
    new_name = sha1(str(path).encode()).hexdigest()
    return _TEMP_DIR / new_name


class Savable(Protocol):
    @property
    def filename(self) -> str | None: ...
    def save(self, dst: PathLike[str]): ...


def save_to_temp_folder(files: Sequence[Savable]):
    _TEMP_DIR.mkdir(exist_ok=True)
    directory = Path(mkdtemp(dir=_TEMP_DIR))
    size = len(files)

    for i, file in enumerate(files, start=1):
        name = str(i).zfill(len(str(size)))
        name += "-" + file.filename if file.filename else ""
        file.save(directory / name)

    return str(directory)
