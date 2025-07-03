import os

from flask import Flask, render_template  # type:ignore

from backend.routes import register_routes

# compute project_root/
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# point to frontend/ for templates
TEMPLATES = os.path.join(BASE, "frontend")

# where to save uploads
UPLOAD_DIR = os.environ.get("UPLOAD_FOLDER", "/tmp/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__, template_folder=TEMPLATES)
app.config["UPLOAD_FOLDER"] = UPLOAD_DIR

# register /predict route
register_routes(app)


# serve the upload form at /
@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
