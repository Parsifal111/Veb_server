import argparse
import os
import json
import logging
from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.exceptions import HTTPException
from werkzeug.utils import secure_filename
from passlib.apache import HtpasswdFile

app = Flask(__name__)
auth = HTTPBasicAuth()

htpasswd = None

def setup_htpasswd():
    global htpasswd
    if htpasswd is None:
        htpasswd_path = app.config['HTPASSWD_PATH']
        try:
            if not os.path.exists(htpasswd_path):
                create_htpasswd_on_first_run(htpasswd_path)
                create_log_file(f"Created htpasswd file at: {htpasswd_path}")
            htpasswd = HtpasswdFile(htpasswd_path)
        except (FileNotFoundError, IOError, PermissionError) as e:
            print(f"Error accessing the file or I/O while reading the htpasswd file:", {e})
        except OSError as e:
            print(f"Operating system error: {e}")
        except Exception as e:
            print(f"Error creating htpasswd file:", {e})

def create_htpasswd_on_first_run(htpasswd_path):
    with HtpasswdFile(htpasswd_path, new=True) as htpasswd_file:
        htpasswd_file.set_password("admin", "12345")
        os.chmod(htpasswd_path, 0o644)  # Устанавливаем права доступа

def create_app_config(directory, config_path, htpasswd_path):
    config = {
        'UPLOAD_FOLDER': directory,
        'HTPASSWD_PATH': htpasswd_path
    }
    with open(config_path, 'w') as f:
        json.dump(config, f)

def create_log_file(message):
    logging.basicConfig(filename='system.log', level=logging.INFO)
    logging.info(message)

@app.before_request
def before_request():
    setup_htpasswd()

@auth.verify_password
def verify_password(username, password):
    if htpasswd:
        try:
            return htpasswd.check_password(username, password)
        except KeyError:
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
        return jsonify({"error": str(ae)}), 500 #Внутренняя ошибка сервера
    except HTTPException as he:
         return jsonify({"error": str(he)}), 500  # Обработка HTTP исключения
    except RuntimeError as re:
        return jsonify({"error": str(re)}), 500  # Обработка RuntimeError
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_data', methods=['GET'])
def get_data():
    # Обработки GET запроса
    return jsonify({"message": "This is a GET request!"})

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({"message": "The server is running normally"})

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Web server')
    parser.add_argument('-p', '--port', type=int, default=5000, help='The port for starting the server (by default 5000)')
    parser.add_argument('-d', '--directory', type=str, default='uploads', help='The directory for uploading files (by default "uploads")')
    parser.add_argument('-c', '--config', type=str, default='app.config', help='The path to the app config file (by default "app.config")')
    args = parser.parse_args()

    app.config['UPLOAD_FOLDER'] = args.directory
    app.config['HTPASSWD_PATH'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'htpasswd')

    if not os.path.exists(args.config):
        create_app_config(args.directory, args.config, app.config['HTPASSWD_PATH'])

    app.run(debug=True, port=args.port)





