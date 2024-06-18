from flask import Flask

def create_app():
    app = Flask(__name__)

    with app.app_context():
        from producer import redis_api_bp
        app.register_blueprint(redis_api_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port='5000', debug=True)

