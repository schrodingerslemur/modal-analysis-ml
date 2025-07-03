import os

from flask import jsonify, request, render_template  # type:ignore
from werkzeug.utils import secure_filename  # type:ignore

from scripts.main import main


def register_routes(app):
    @app.route("/predict", methods=["POST"])
    def predict():
        dat_file = request.files.get("dat_file")
        inp_file = request.files.get("inp_file")

        if not dat_file or not inp_file:
            return render_template("result.html", error="Please upload both files.", result=None), 400

        # secure filenames
        dat_name = secure_filename(dat_file.filename)
        inp_name = secure_filename(inp_file.filename)

        # saves to ../data
        upload_dir = app.config["UPLOAD_FOLDER"]
        dat_path = os.path.join(upload_dir, dat_name)
        inp_path = os.path.join(upload_dir, inp_name)

        # save uploads
        dat_file.save(dat_path)
        inp_file.save(inp_path)

        try:
            result = main(dat_path, inp_path)
            print(type(result))
            # pass result dict to template
            table_html = result["Results"].to_html(classes="table table-striped", index=False)
            return render_template("result.html", result=table_html, modal_target=result.get("Modal Separation Target"), \
                                   inplane_modes=result.get("Inplane modes"), out_of_plane_modes=result.get("Out-of-plane modes"), \
                                   error=None)

        except Exception as e:
            return render_template("result.html", error=str(e), result=None), 500