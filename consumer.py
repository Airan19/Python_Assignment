import redis
import time

# Connecting to Redis
r_conn = redis.Redis(host='redis', port=6379, db=0)

# Enable Key Space Notifications for the 'employee' key
r_conn.config_set('notify-keyspace-events', 'KEA')

# Create a pubsub object
pubsub = r_conn.pubsub()

# Subscribe to keyspace notifications for 'employee' key in database 0
pubsub.psubscribe('__keyspace@0__:employee:*')

print("----------------CONSUMER--------------------")

def log_change(event, key, data):
    with open('employee_log.txt', 'a') as log_file:
        log_file.write(f"{time.ctime()}: {event} - Key: {key}  Data: {data} \n")
    
# Listen for messages
for message in pubsub.listen():
    try:
        # Key event notification
        if message['type'] == 'pmessage':
            event = message['data'].decode('utf-8') if isinstance(message['data'], bytes) else str(message['data'])
            key = message['channel'].decode('utf-8').split(':')[-1]
            # if event in ['json.set', 'del']:
                # old_data = r_conn.json().get(f"employee:{key}")
                # old_data = json.dumps(old_data) if old_data else 'None'

                # if event == 'json.set':
                #     new_data = r_conn.json().get(f"employee:{key}")
                #     new_data = json.dumps(new_data) if new_data else 'None'
                # else:
                #     new_data = 'Deleted'
            data = r_conn.json().get(f"employee:{key}")

            log_change(event, key, data)
            print(f"Logged change: {event} - Key: {key}  Data: {data}")
    except Exception as e:
        print(f"Error processing message: {e}")