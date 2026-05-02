from collections.abc import Callable
from functools import lru_cache
import os
from zipfile import BadZipFile, ZipFile

from temp import temp_name_for


@lru_cache
def unzip_file(file: str):
    directory = str(temp_name_for(file))
    with ZipFile(file, "r") as archive:
        archive.extractall(directory)
    return directory


@lru_cache
def get_first_file(file: str | os.PathLike, filter_fn: Callable[[str], bool]):
    directory = str(temp_name_for(file))
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
