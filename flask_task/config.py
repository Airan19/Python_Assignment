from os import getenv, environ
from dotenv import load_dotenv


load_dotenv('env')

class Config:

    PORT_LOAD = "5000"


class ProdConfig(Config):
    #Database Configuration
    DB_NAME = getenv('DB_NAME')
    DB_USER = getenv('DB_USER')
    DB_PASSWORD = getenv('DB_PASSWORD')
    DB_SERVER = getenv('DB_SERVER')
    DB_PORT = getenv('DB_PORT')
    DB_MASTER = getenv('DB_MASTER')
    # Check if running in Docker environment
    if getenv('DOCK ER_ENV') == 'true':
        # If running in Docker, include port
        DB_SERVER += ',' + DB_PORT


def get_configs(app):
    if app:
        return app.config   
    return environ