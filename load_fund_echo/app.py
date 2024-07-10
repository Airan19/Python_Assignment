from flask import Flask

def create_app():
    app = Flask(__name__)

    with app.app_context():
        # Import and register the Blueprint for the API routes
        from routes import api_bp
        app.register_blueprint(api_bp)

    return app


if __name__ == "__main__":
    # Create an instance of the Flask app
    app = create_app()

    # Run the Flask app on the specified host and port with debugging enabled
    app.run(host='0.0.0.0', port='6020', debug=True)

