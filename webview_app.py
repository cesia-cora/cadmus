from django.core.wsgi import get_wsgi_application
import os
import sys
import threading
import webview
from waitress import serve

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'diary.settings')

def start_server():
    application = get_wsgi_application()
    serve(application, host='127.0.0.1', port=8000, threads=4)

if __name__ == '__main__':
    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    webview.create_window('Cadmus | Personal Diary', 'http://127.0.0.1:8000', width=1024, height=768)
    webview.start(icon='diary/cadmus/static/cadmus/icon.ico')