import argparse
import os
from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.exceptions import HTTPException
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
     # Обработка ошибки отсутствия файла, ошибки ввода-вывода или ошибки доступа
    except (FileNotFoundError, IOError, PermissionError) as e:
        print(f"Error accessing the file or I/O while reading the htpasswd file:", {e})
        return None
    except OSError as e:
        #Обработка ошибок операционной системы
        print(f"Operating system error: {e}")
        return None
    
@auth.verify_password
def verify_password(username, password):
    htpasswd = setup_htpasswd()
    if htpasswd:
        try:
            return htpasswd.check_password(username, password)
        except KeyError:
            #Обработка отсутствия ключа (Имени пользователя в файле htpasswd)
            print(f"username '{username}' not found in the htpasswd file")
            return False
    return False

@app.route('/upload', methods=['POST'])
@auth.login_required
def upload_file():
    try:
        # Попытка получить файл из запроса
        file = request.files['file']
    except KeyError:
        #Обработка отсутствия ключа (файла) в запросе
        return jsonify({"error": "The file was not attached to the request"}), 400
    try:
        if file.filename == '':
            raise ValueError("The file name is empty")
        
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({"message": "The file has been uploaded successfully!"})
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400  # Плохой запрос
    except AttributeError as ae:
        return jsonify({"error": str(e)}), 500 #Внутренняя ошибка сервера
    except HTTPException as he:
         return jsonify({"error": str(he)}), he.code  # Обработка HTTP исключения
    except RuntimeError as re:
        return jsonify({"error": str(re)}), 500  # Обработка RuntimeError
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description='Web server')
        parser.add_argument('-p', '--port', type=int, default=5000, help='The port for starting the server (by default 5000)')
        parser.add_argument('-d', '--directory', type=str, default='uploads', help='The directory for uploading files (by default "uploads")')
        parser.add_argument('-f', '--htpasswd', type=str, default='htpasswd', help='The path to the file htpasswd (by default "htpasswd")')
        args = parser.parse_args()
    except argparse.ArgumentError as ae:
        print(f"Error processing command line arguments: {ae}")

    app.config['UPLOAD_FOLDER'] = args.directory
    app.config['HTPASSWD_PATH'] = args.htpasswd

    app.run(debug=True, port=args.port)
