from pathlib import Path
import secrets

import flask

from fileutils import dir_entries, list_images_from_folder
from unzip import unzip_file

SUPPORTED_FILES = {".zip", ".cbz", "epub"}
app = flask.Flask(__name__)
app.secret_key = secrets.SystemRandom().randbytes(100000)


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


@app.get("/picker")
def index():
    path = flask.request.args.get("path", str(Path.home()), type=str)
    entries, prev = dir_entries(path, SUPPORTED_FILES)
    return flask.render_template(
        "picker.html", entries=entries, current=path, prev=prev
    )


@app.get("/file/<path:file>")
def file(file: str):
    # TODO: handle permissions
    path = Path("/" + file)
    return flask.send_from_directory(path.parent, path.name, as_attachment=False)


@app.get("/unzip")
def unzip():
    file = flask.request.args.get("file", type=str)
    if not file:
        return flask.redirect("/picker")

    if Path(file).is_dir():
        # Already a directory, nothing to decompress
        descompressed_path = file
    else:
        descompressed_path = unzip_file(file)

    return flask.redirect(
        "/reader?file=" + descompressed_path + "&orignal_path=" + file
    )


@app.get("/reader")
def reader():
    folder = flask.request.args.get("file", type=str)
    if not folder:
        return flask.redirect("/picker")

    # TODO: maybe we should check if the entries contain any *files*
    # We get the original path since we open files on a temp folder but we
    # want to show the directory from the original file.
    og_path = flask.request.args.get("orignal_path", folder, type=str)

    # Re-uncompress the zip if the user bookmark the link and the temp folder is gone
    if not Path(folder).exists() and og_path:
        return flask.redirect(
            f"/unzip?file={og_path}&page=" + flask.request.args.get("page", "")
        )

    pages = ["/file" + img for img in list_images_from_folder(folder)]
    entries, _ = dir_entries(str(Path(og_path).parent), SUPPORTED_FILES)

    return flask.render_template(
        "reader.html", pages=pages, entries=entries, current=og_path
    )


app.run("0.0.0.0", debug=True)
