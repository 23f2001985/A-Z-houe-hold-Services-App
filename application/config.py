import os
basedir = os.path.abspath(os.path.dirname(__file__))
class Config:
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False
class LocalDevelopmentConfig(Config):
    SQLITE_DB_DIR = os.path.join(basedir, "..", "db_directory")
    if not os.path.exists(SQLITE_DB_DIR):
        os.makedirs(SQLITE_DB_DIR)
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(SQLITE_DB_DIR, 'mydb.sqlite3')}"
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    SESSION_TYPE = 'null' 
