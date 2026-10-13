from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from app.models import db, User
import os

load_dotenv()

bcrypt = Bcrypt()
login_manager = LoginManager()
csrf = CSRFProtect()

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'templates'
        ),
        static_folder=os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'static'
        )
    )

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    if not app.config['SECRET_KEY']:
        raise RuntimeError(
            'SECRET_KEY environment variable is not set.'
        )

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'sqlite:///codehelp.db'
    )

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    is_production = os.getenv('FLASK_ENV') == 'production'

    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = is_production

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'

    from app.auth import auth as auth_blueprint
    app.register_blueprint(
        auth_blueprint,
        url_prefix='/auth'
    )

    from app.routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    with app.app_context():
        db.create_all()

    @app.route('/health')
    def health():
        return {
            'status': 'ok',
            'app': 'CodeHelp'
        }

    return app