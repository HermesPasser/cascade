from collections.abc import Callable
from functools import lru_cache
import os
from zipfile import BadZipFile, ZipFile

from temp import temp_name_for


def unzip_file(file: str):
    temp = temp_name_for(file)
    directory = str(temp)
    if temp.exists():
        return directory

    with ZipFile(file, "r") as archive:
        archive.extractall(directory)
    return directory


def get_first_file(file: str | os.PathLike, filter_fn: Callable[[str], bool]):
    temp = temp_name_for(file)
    directory = str(temp)
    if temp.exists():
        return directory

    try:
        with ZipFile(file, "r") as archive:
            it = filter(filter_fn, sorted((f.filename for f in archive.filelist)))
            filename = next(it, None)
            if filename:
                archive.extract(filename, directory)
                return os.path.join(directory, filename)

        return None
    except BadZipFile:
        return None
