from flask import Flask
from waitress import serve
from scheduler import scheduler
import time
import pymssql


def create_app(env):
    app = Flask(__name__)
    app.config.from_object(env) 

    with app.app_context():
        # Register blueprints
        from routes import web_api_bp
        app.register_blueprint(web_api_bp)

    return app


# Wait for MSSQL server to be ready   
def wait_for_mssql(app):
    configs = app.config
    server = configs['DB_SERVER']
    user = configs['DB_USER']
    password = configs['DB_PASSWORD']
    main_db = configs['DB_MASTER']
    max_retries = 10
    retries = 0
    wait_time = 5

    while retries < max_retries:
        try:    
            pymssql.connect(server=server, user=user, password=password, database=main_db)
            print('Mssql Server is up and connection is established.')
            return True
        except:
            retries += 1
            print(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
            
    print("Max retries reached. Unable to connect to MSSQL server.")
    return False


if __name__ == "__main__":
    env_ = 'config.ProdConfig'
    _app = create_app(env_)

    if not wait_for_mssql(_app):
        print("Database initialization failed. Exiting...")
        raise RuntimeError("Failed to connect to the database.")

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



