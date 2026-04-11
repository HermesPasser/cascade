from pathlib import Path

import flask

from fileutils import dir_entries

app = flask.Flask(__name__)


# TODO: make reader
# TODO: make reader read files
@app.get("/")
def home():
    return flask.redirect("/picker")


@app.get("/picker")
def index():
    path = flask.request.args.get("path", str(Path.home()), type=str)
    entries, prev = dir_entries(path)
    return flask.render_template(
        "picker.html", entries=entries, current=path, prev=prev
    )


@app.get("/file/<path:file>")
def file(file: str):
    path = Path("/" + file)
    return flask.send_from_directory(path.parent, path.name, as_attachment=False)


@app.get("/reader")
def reader():
    return flask.render_template("reader.html")


app.run("0.0.0.0", debug=True)
