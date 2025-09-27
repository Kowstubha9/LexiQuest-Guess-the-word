from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from lexiquest_app.config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    from lexiquest_app.routes import bp as main_bp 
    app.register_blueprint(main_bp)
    
    with app.app_context():
        import lexiquest_app.models 
        db.create_all() 

    return app