from functools import lru_cache
import tempfile
from zipfile import ZipFile


@lru_cache
def unzip_file(file: str):
    directory = tempfile.mkdtemp()
    ZipFile(file).extractall(directory)
    return directory
