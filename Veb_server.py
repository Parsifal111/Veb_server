from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
import os 

app = Flask(__name__)
auth = HTTPBasicAuth()

# Простой словарь с пользователями и паролями (лучше хранить в базе данных)
users = {
    "admin": "password"
}

@auth.verify_password
def verify_password(username, password):
    if username in users and password == users[username]:
        return username

@app.route('/upload', methods=['POST'])
@auth.login_required
def upload_file():
    try:
        file = request.files['file']
        # Сохраняем файл на сервере или обрабатываем его
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({"message": "Файл успешно загружен!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = 'uploads'
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)