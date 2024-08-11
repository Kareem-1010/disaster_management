from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from config import Config
from models import User
from extensions import db

login_manager = LoginManager()
login_manager.login_view = 'main.login'
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        from routes import main_bp
        app.register_blueprint(main_bp)
        db.create_all()

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)