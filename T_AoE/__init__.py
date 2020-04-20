from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_user import UserManager

db = SQLAlchemy()
mail = Mail()


def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')
    db.init_app(app)
    mail.init_app(app)
    from .routes import register_blueprints
    register_blueprints(app)
    from .models import User
    user_manager = UserManager(app, db, User)
    @app.context_processor
    def context_processor():
        return dict(user_manager=user_manager)
    return app
