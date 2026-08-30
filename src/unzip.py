from collections.abc import Callable
from functools import lru_cache
import os
from pathlib import Path
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
    # Before generating the temp name we strip the original folder the file was
    # contained in. Prevents the placing of the thumbnail in the same temp folder
    # the reader will try to uncompress, that would cause the reader to only display
    # the thumbnail since it only decompress if the folder does not exists.
    file_without_dir = Path(file).name

    temp = temp_name_for(file_without_dir)
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
