from flask import Flask
from config import Config, get_configs

def create_app(config_class):
    app = Flask(__name__)

    # Load configuration from the provided config class
    app.config.from_object(config_class)

    with app.app_context():
        # Import and register the Blueprint for the Redis API routes
        from producer import redis_api_bp
        app.register_blueprint(redis_api_bp)

    return app

if __name__ == "__main__":
    # Create an instance of the Flask app with the specified configuration
    app = create_app(Config)
    
    # Run the Flask app on the specified host and port with debugging enabled
    app.run(host='0.0.0.0', port='5000', debug=True)

