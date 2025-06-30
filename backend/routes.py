import os
from flask import request, jsonify, current_app #type:ignore
from werkzeug.utils import secure_filename #type:ignore
from scripts.main import main  

def register_routes(app):
    @app.route('/predict', methods=['POST'])
    def predict():
        dat_file = request.files.get('dat_file')
        inp_file = request.files.get('inp_file')

        if not dat_file or not inp_file:
            return jsonify({'error': 'Please upload both files.'}), 400

        # secure filenames
        dat_name = secure_filename(dat_file.filename)
        inp_name = secure_filename(inp_file.filename)

        # saves to ../data
        upload_dir = app.config['UPLOAD_FOLDER']
        dat_path = os.path.join(upload_dir, dat_name)
        inp_path = os.path.join(upload_dir, inp_name)

        # save uploads
        dat_file.save(dat_path)
        inp_file.save(inp_path)

        try:
            result = main(dat_path, inp_path)
            return jsonify({'result': result})
        except Exception as e:
            # optional: clean up saved files here if you want
            return jsonify({'error': str(e)}), 500
