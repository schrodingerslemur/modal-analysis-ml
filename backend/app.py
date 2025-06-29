import os
from flask import Flask, render_template #type:ignore
from backend.routes import register_routes

# compute project_root/
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# point to frontend/ for your templates
TEMPLATES = os.path.join(BASE, 'frontend')

# where you want to save uploads
UPLOAD_DIR = os.path.join(BASE, 'data')

app = Flask(
    __name__,
    template_folder=TEMPLATES
)
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR

# register your /predict route
register_routes(app)

# serve the upload form at /
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
