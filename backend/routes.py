from flask import request, jsonify #type:ignore
from scripts import main  

def register_routes(app):
    @app.route('/predict', methods=['POST'])
    def predict():
        dat_file = request.files.get('dat_file')
        inp_file = request.files.get('inp_file')

        if not dat_file or not inp_file:
            return jsonify({'error': 'Please upload both files.'}), 400

        try:
            result = main(dat_file, inp_file)
            return jsonify({'result': result})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
