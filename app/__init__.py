from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from dotenv import load_dotenv
from app.models import db, User
import os

load_dotenv()

bcrypt = Bcrypt()
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__,template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'),
            static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'))

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-dev-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL', 'sqlite:///codehelp.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'

    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    with app.app_context():
        db.create_all()

    @app.route('/health')
    def health():
        return {'status': 'ok', 'app': 'CodeHelp'}

    return app