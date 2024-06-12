import redis
import time
import json
from redis.commands.json.path import Path

# Creating a connection with Redis
r_conn = redis.Redis(host='redis', port=6379, db=0)

# Open the employee data file
with open('employee_data.json') as f:
    employee_data = json.load(f)

for data in employee_data:
    # Update the JSON object with the new employee data
    employee_key = f"employee:{data['id']}"
    # employee = json.dumps(data)
    r_conn.json().set(employee_key, Path.root_path(), data)
    print(f'Produced {data}')
    time.sleep(5)

print('JSON Get Key 1', r_conn.json().get("employee:1"))
time.sleep(5)
print('Deleting Key 2', bool(r_conn.json().delete("employee:2")))