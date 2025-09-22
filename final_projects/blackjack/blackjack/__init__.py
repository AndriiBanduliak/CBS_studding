import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()

# Import logger
from blackjack.logger import logger

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    # Default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///blackjack.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        MAIL_SERVER=os.environ.get('MAIL_SERVER', 'smtp.gmail.com'),
        MAIL_PORT=int(os.environ.get('MAIL_PORT', 587)),
        MAIL_USE_TLS=os.environ.get('MAIL_USE_TLS', True),
        MAIL_USERNAME=os.environ.get('MAIL_USERNAME'),
        MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD'),
        MAIL_DEFAULT_SENDER=os.environ.get('MAIL_DEFAULT_SENDER')
    )

    # Override config with test config if passed
    if test_config:
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    mail.init_app(app)
    migrate.init_app(app, db)
    
    # Import models
    from . import models
    
    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(int(user_id))
    
    # Register blueprints
    from .auth import auth_bp
    app.register_blueprint(auth_bp)
    
    from .main import main_bp
    app.register_blueprint(main_bp)
    
    from .game import game_bp
    app.register_blueprint(game_bp)
    
    return app

    # Register blueprints
    from blackjack.auth import auth_bp
    app.register_blueprint(auth_bp)

    from blackjack.main import main_bp
    app.register_blueprint(main_bp)

    from blackjack.game import game_bp
    app.register_blueprint(game_bp)

    # Shell context
    @app.shell_context_processor
    def make_shell_context():
        return {'db': db, 'app': app}

    return app