from pathlib import Path
import secrets
import socket
import subprocess
import sys
from urllib.parse import quote, unquote

import flask

from fileutils import (
    SUPPORTED_ARCHIVE_EXTENSIONS,
    dir_entries,
    downsize,
    list_images_from_folder,
)
from temp import save_to_temp_folder
from unzip import unzip_file

app = flask.Flask(__name__)
app.secret_key = secrets.SystemRandom().randbytes(100000)
app.jinja_env.filters["quote"] = lambda u: quote(u, safe="/")
HOST_LOCAL_IP = socket.gethostbyname("localhost")


@app.errorhandler(FileNotFoundError)
@app.errorhandler(ValueError)
def not_found(e):
    message = e.filename if isinstance(e, FileNotFoundError) else e
    flask.flash(f"Not found: {message}")
    return flask.redirect("/")


# TODO: make reader read files (rar, etc)
@app.get("/")
def home():
    return flask.redirect("/picker")


@app.post("/paste")
def paste():
    files = list(flask.request.files.values())
    if not files:
        return "No files given", 400

    folder = save_to_temp_folder(files)

    # In case of the user having dragged an archive, then pass the archive's path
    # to the unzip route instead of opening the containing temp folder
    if (
        files
        and files[0].filename
        and any(
            True
            for e in SUPPORTED_ARCHIVE_EXTENSIONS
            if files[0].filename.endswith(f".{e}")
        )
    ):
        folder = next(Path(folder).iterdir())
        return flask.redirect(f"/unzip?file={folder}")

    return flask.redirect(f"/reader?file={folder}&original_path={Path.home()}")


@app.get("/picker")
def index():
    client_is_on_localhost = int(flask.request.remote_addr == HOST_LOCAL_IP)
    path = flask.request.args.get("path", str(Path.home()), type=str)
    entries, prev = dir_entries(path)
    return flask.stream_template(
        "picker.html",
        entries=entries,
        current=path,
        prev=prev,
        localhost=HOST_LOCAL_IP + ":5000",
        client_is_on_localhost=client_is_on_localhost,
    )


@app.post("/open/<path:file>")
def open_on_filesystem(file: str):
    unquoted = unquote("/" + file)
    if sys.platform == "win32":
        command = "explorer"
    elif sys.platform == "linux":
        command = "xdg-open"
    else:
        command = None

    if command:
        subprocess.run([command, unquoted])

    return {}, 204


@app.get("/file/<path:file>")
def file(file: str):
    # TODO: handle permissions
    unquoted = unquote("/" + file)
    mode = flask.request.args.get("mode")
    path = Path(downsize(unquoted) if mode == "thumb" else unquoted)
    return flask.send_from_directory(path.parent, path.name, as_attachment=False)


@app.get("/unzip")
def unzip():
    file = flask.request.args.get("file", type=str)
    if not file:
        flask.flash("No file provided")
        return flask.redirect("/picker")

    if Path(file).is_dir():
        # Already a directory, nothing to decompress
        descompressed_path = file
    else:
        descompressed_path = unzip_file(file)

    page = flask.request.args.get("page", "")
    return flask.redirect(
        "/reader?file="
        + descompressed_path
        + "&original_path="
        + quote(file)
        + "&page="
        + page
    )


@app.get("/reader")
def reader():
    folder = flask.request.args.get("file", type=str)
    if not folder:
        flask.flash("No folder provided")
        return flask.redirect("/picker")

    folder = unquote(folder)
    # TODO: maybe we should check if the entries contain any *files*
    # We get the original path since we open files on a temp folder but we
    # want to show the directory from the original file.
    og_path = flask.request.args.get("original_path", folder, type=str)

    # Re-uncompress the zip if the user bookmark the link and the temp folder is gone
    if not Path(folder).exists() and og_path:
        flask.flash("Neither temp folder nor original folder exists")
        return flask.redirect(
            f"/unzip?file={quote(og_path)}&page="
            + flask.request.args.get("page", "")
        )

    pages = ["/file" + quote(img) for img in list_images_from_folder(folder)]
    parent = str(Path(og_path).parent)
    entries, _ = dir_entries(parent)

    if not pages:
        flask.flash("Directory/archive has no images")
        return flask.redirect("/")

    client_is_on_localhost = int(flask.request.remote_addr == HOST_LOCAL_IP)
    return flask.render_template(
        "reader.html",
        pages=pages,
        entries=entries,
        current=og_path,
        parent=parent,
        client_is_on_localhost=client_is_on_localhost,
    )


all_hosts = "--all-hosts" in sys.argv
app.run(host="0.0.0.0" if all_hosts else "localhost", debug=not all_hosts)
