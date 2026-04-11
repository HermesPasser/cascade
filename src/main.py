from pathlib import Path

import flask

from fileutils import dir_entries, list_images_from_folder
from unzip import unzip_file

app = flask.Flask(__name__)


# TODO: make reader read files (rar, etc)
@app.get("/")
def home():
    return flask.redirect("/picker")


@app.get("/picker")
def index():
    path = flask.request.args.get("path", str(Path.home()), type=str)
    entries, prev = dir_entries(path, {".zip", ".cbz", "epub"})
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

    decompressed_path = unzip_file(file)
    return flask.redirect("/reader?file=" + decompressed_path)


@app.get("/reader")
def reader():
    folder = flask.request.args.get("file", type=str)
    if not folder:
        return flask.redirect("/picker")

    pages = ["/file" + img for img in list_images_from_folder(folder)]
    return flask.render_template("reader.html", pages=pages)


app.run("0.0.0.0", debug=True)
