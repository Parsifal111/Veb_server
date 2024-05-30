import argparse
import os
from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.utils import secure_filename
from passlib.apache import HtpasswdFile

app = Flask(__name__)
auth = HTTPBasicAuth()

@app.before_first_request
def setup_htpasswd():
    htpasswd_path = app.config['HTPASSWD_PATH']
    try:
        if not os.path.exists(htpasswd_path):
            open(htpasswd_path, 'a').close()
        return HtpasswdFile(htpasswd_path)
    except IOError as ioe:
        #Обработка ошибки ввода-вывода при чтении файла
        print("I/O error when reading htpasswd file:", ioe)
        return None
    
@auth.verify_password
def verify_password(username, password):
    htpasswd = setup_htpasswd()
    if htpasswd:
        return htpasswd.check_password(username, password)
    return False

@app.route('/upload', methods=['POST'])
@auth.login_required
def upload_file():
    try:
        if 'file' not in request.files:
            raise ValueError("The file was not attached to the request")
        
        file = request.files['file']
        
        if file.filename == '':
            raise ValueError("The file name is empty")
        
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({"message": "The file has been uploaded successfully!"})
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400  # Плохой запрос
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Web server')
    parser.add_argument('-p', '--port', type=int, default=5000, help='The port for starting the server (by default 5000)')
    parser.add_argument('-d', '--directory', type=str, default='uploads', help='The directory for uploading files (by default "uploads")')
    parser.add_argument('-f', '--htpasswd', type=str, default='htpasswd', help='The path to the file htpasswd (by default "htpasswd")')
    args = parser.parse_args()

    app.config['UPLOAD_FOLDER'] = args.directory
    app.config['HTPASSWD_PATH'] = args.htpasswd

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    app.run(debug=True, port=args.port)
