from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
import os

# Create extensions without initializing them
db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Initialize extensions with the app
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Import and register blueprints
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app