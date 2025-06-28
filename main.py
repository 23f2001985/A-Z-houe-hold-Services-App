import os
from flask import Flask
from application import config
from application.config import LocalDevelopmentConfig
from application.database import db
app = None
def create_app():
    global app
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.secret_key = os.urandom(24)
    if os.getenv('ENV', "development") == "production":
        raise Exception("Currently no production config is set up.")
    else:
        print("Starting Local Development")
        app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    with app.app_context():
        db.create_all()  
    app.app_context().push()
    return app
app = create_app()
print(app.config['SQLALCHEMY_DATABASE_URI'])
from application.controllers import *
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
