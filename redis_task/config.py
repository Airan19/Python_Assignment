import os
from dotenv import load_dotenv

load_dotenv('../environ_file')

class Config:
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_SERVER = os.getenv('DB_SERVER')
    DB_PORT = os.getenv('DB_PORT')
    DB_MASTER = os.getenv('DB_MASTER')

    REDIS_HOST = os.getenv('REDIS_HOST', 'redis-container')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

def get_configs(app):
    if app:
        return app.config   
    return os.environ