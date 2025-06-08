from flask import Flask, render_template, request, send_from_directory, jsonify
from flask_socketio import SocketIO, emit
import os, shutil, requests
from bs4 import BeautifulSoup
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads'

app = Flask(__name__)
socketio = SocketIO(app)

# サーバー起動時にuploadsフォルダを空にする
if os.path.exists(UPLOAD_FOLDER):
    shutil.rmtree(UPLOAD_FOLDER)
os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/preview')
def preview():
    url = request.args.get('url')
    try:
        resp = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(resp.text, 'html.parser')
        def get(prop):
            tag = soup.find('meta', property=prop)
            return tag['content'] if tag and 'content' in tag.attrs else ''
        return jsonify({
            'title': get('og:title') or soup.title.string if soup.title else '',
            'description': get('og:description') or '',
            'image': get('og:image') or ''
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@socketio.on('message')
def handle_message(data):
    emit('message', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
