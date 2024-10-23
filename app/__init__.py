#__init__.py file
from flask import Flask
from flask_restful import Api
from app.models import db, User
from flask_login import LoginManager, current_user
from app.resources import TaskResource

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

    db.init_app(app)
    api = Api(app)

    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.context_processor
    def inject_user():
        return dict(current_user=current_user)
    
    api.add_resource(TaskResource, '/api/tasks', '/api/tasks/<int:task_id>')

    return app
