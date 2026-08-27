from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-dev-key')

    @app.route('/health')
    def health():
        return {'status': 'ok', 'app': 'CodeHelp'}

    return app