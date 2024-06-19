import redis
import time
import json
from db import DatabaseManager
from config import get_configs
from flask import current_app as app


def configure_database():
    configs = get_configs(app)
    DB_NAME = configs.get('DB_NAME')
    DB_USER = configs.get('DB_USER')
    DB_PASSWORD = configs.get('DB_PASSWORD')
    DB_SERVER = configs.get('DB_SERVER')
    DB_PORT = configs.get('DB_PORT')
    DB_MASTER = configs.get('DB_MASTER')
    return DB_NAME, DB_USER, DB_PASSWORD, DB_SERVER, DB_PORT, DB_MASTER


def create_redis_connection():
    configs = get_configs(app)
    REDIS_HOST = configs.get('REDIS_HOST', 'redis-container')
    REDIS_PORT = int(configs.get('REDIS_PORT', 6379))

    r_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    r_conn.config_set('notify-keyspace-events', 'KEA')
    pubsub = r_conn.pubsub()
    pubsub.psubscribe('__keyspace@0__:employee/*')

    return r_conn, pubsub


def execute_sql_query(query, params=None, fetchone=False, fetchall=False):
    DB_NAME, DB_USER, DB_PASSWORD, DB_SERVER, DB_PORT, DB_MASTER = configure_database()
    with DatabaseManager(server=DB_SERVER, user=DB_USER, password=DB_PASSWORD, 
                         database=DB_NAME, main_db=DB_MASTER, port=DB_PORT) as sql_db:
        output = sql_db.execute_query(query, params, fetchone, fetchall)
        return output


def log_change(event, key, data):
    with open('employee_log.txt', 'a') as log_file:
        log_file.write(f"{time.ctime()}: {event} - Key: {key}  Data: {data} \n")


def handle_set_action(r_conn, key):
    data = r_conn.get(f"employee/{key}")
    data = data.decode('utf-8') if isinstance(data, bytes) else print(type(data))
    # print(data, type(data))
    if isinstance(data, str):
        data = json.loads(r_conn.get(f"employee/{key}"))
    if data:
        query = """
        IF EXISTS (SELECT 1 FROM Employees WHERE emp_id=%s)
        UPDATE Employees
        SET name=%s, gender=%s, phone=%s, department=%s, date_of_birth=%s, email=%s, experience=%s
        WHERE emp_id=%s
        ELSE
        INSERT INTO Employees (emp_id, name, gender, phone, department, date_of_birth, email, experience)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            data["emp_id"], data['name'], data['gender'], data['phone'], data['department'],
            data['date_of_birth'], data['email'], data['experience'], data['emp_id'], data['emp_id'],
            data['name'], data['gender'], data['phone'], data['department'],
            data['date_of_birth'], data['email'], data['experience']
        ) 
        res = execute_sql_query(query, params)
        print('res', res)


def handle_delete_action(key):
    employee_id = int(key)
    query = "DELETE FROM Employees WHERE id=%s"
    params = (employee_id)
    res = execute_sql_query(query, params)
    print('res', res)


def listen_for_messages():
    r_conn, pubsub = create_redis_connection()
    for message in pubsub.listen():
        try:
            if message['type'] == 'pmessage':
                event = message['data'].decode('utf-8') if isinstance(message['data'], bytes) else str(message['data'])
                key = message['channel'].decode('utf-8').split('/')[-1]
                if event == 'set':
                    handle_set_action(r_conn, key)
                elif event == 'del':
                    handle_delete_action(key)
                data = r_conn.get(f"employee/{key}")

                log_change(event, key, data)
                print(f"Logged change: {event} - Key: {key}  Data: {data}")
        except Exception as e:
            print(f"Error processing message: {e}")


if __name__ == "__main__":
    print("----------------CONSUMER--------------------")
    listen_for_messages()
