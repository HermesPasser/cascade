
import flask


app = flask.Flask(__name__)


# TODO: list folders
# TODO: open files and folders
# TODO: make reader
# TODO: make reader read files
@app.get("/")
def home():
    return {"message": "hello, world"}, 200



app.run("0.0.0.0", debug=True)
