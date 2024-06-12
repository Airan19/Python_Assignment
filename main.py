from flask import Flask
from waitress import serve
from scheduler import scheduler


def create_app(env):
    app = Flask(__name__)
    app.config.from_object(env) 

    with app.app_context():
        # Register blueprints
        from routes import web_api_bp
        app.register_blueprint(web_api_bp)

    return app


if __name__ == "__main__":
    env_ = 'config.ProdConfig'
    _app = create_app(env_)

    try:
        scheduler.init_app(_app)
        scheduler.start()
    except:
        print('Scheduler already running')

    try:
        serve(_app, host='0.0.0.0', port=5000)
    finally:
        if scheduler.running:
            scheduler.shutdown()
            print('Shutting down scheduler')



