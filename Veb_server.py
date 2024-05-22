import argparse
from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.utils import secure_filename
import os 
from passlib.apache import HtpasswdFile

app = Flask(__name__)
auth = HTTPBasicAuth()

# Загрузка пользователей и паролей из файла htpasswd
htpasswd = HtpasswdFile("/path/to/htpasswd")

@auth.verify_password
def verify_password(username, password):
    return htpasswd.check_password(username, password)

@app.route('/upload', methods=['POST'])
@auth.login_required
def upload_file():
    try:
        if 'file' not in request.files:
            raise ValueError("Файл не был прикреплен к запросу")
        
        file = request.files['file']
        
        if file.filename == '':
            raise ValueError("Имя файла пустое")
        
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({"message": "Файл успешно загружен!"})
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400  # Плохой запрос
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Web server')
    parser.add_argument('-p', '--port', type=int, default=5000, help='Порт для запуска сервера (по умолчанию 5000)')
    parser.add_argument('-d', '--directory', type=str, default='uploads', help='Директория для загрузки файлов (по умолчанию "uploads")')
    parser.add_argument('-f', '--htpasswd', type=str, default='htpasswd', help='Путь к файлу htpasswd (по умолчанию "htpasswd")')
    args = parser.parse_args()

    app.config['UPLOAD_FOLDER'] = args.directory
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    htpasswd = HtpasswdFile(args.htpasswd)

    app.run(debug=True, port=args.port)
