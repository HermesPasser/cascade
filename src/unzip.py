from collections.abc import Callable, Iterable
from functools import lru_cache
import os
import tempfile
from zipfile import BadZipFile, ZipFile


@lru_cache
def unzip_file(file: str):
    directory = tempfile.mkdtemp()
    ZipFile(file).extractall(directory)
    return directory


@lru_cache
def get_first_file(file: str | os.PathLike, filter_fn: Callable[[str], bool]):
    directory = tempfile.mkdtemp()
    try:
        archive = ZipFile(file)
        it = filter(filter_fn, sorted((f.filename for f in archive.filelist)))
        filename = next(it, None)
        if filename:
            archive.extract(filename, directory)
            return os.path.join(directory, filename)

        return None
    except BadZipFile:
        return None
