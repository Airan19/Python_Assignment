from flask import Flask
from config import Config, get_configs

def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)

    with app.app_context():
        from producer import redis_api_bp
        app.register_blueprint(redis_api_bp)

    return app

if __name__ == "__main__":
    app = create_app(Config)
    app.run(host='0.0.0.0', port='5000', debug=True)

