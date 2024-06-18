import json
import redis
from os import getenv
from flask import jsonify, Blueprint, request, current_app as app

redis_api_bp = Blueprint('redis_api', __name__)

# Load environment variables
REDIS_HOST = getenv('REDIS_HOST', 'redis-container')
REDIS_PORT = int(getenv('REDIS_PORT', 6379))

# Creating a connection with Redis
r_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

# # Open the employee data file
# with open('employee_data.json') as f:
#     employee_data = json.load(f)

# for data in employee_data:
#     # Update the JSON object with the new employee data
#     employee_key = f"employee:{data['id']}"
#     # employee = json.dumps(data)
#     r_conn.json().set(employee_key, Path.root_path(), data)
#     print(f'Produced {data}')
#     time.sleep(5)

# print('JSON Get Key 1', r_conn.json().get("employee:1"))
# time.sleep(5)
# print('Deleting Key 2', bool(r_conn.json().delete("employee:2")))

print('-----------------------PRODUCER-----------------')

@redis_api_bp.route('/create', methods=['POST'])
def create_employee():  
    data = request.get_json()
    try:
        employee_key = f"employee/{data['emp_id']}"
        if r_conn.get(employee_key) != None:
            return jsonify({'message': f"Employee with emp_id: {data['emp_id']} already exists."})
        r_conn.set(employee_key, (json.dumps(data)))
        return jsonify({'message': 'Employee created successfully'}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@redis_api_bp.route('/update/<int:emp_id>', methods=['PUT'])
def update_employee(emp_id):
    data = request.get_json()
    # try:
    employee_key = f"employee/{emp_id}"
    if data['emp_id'] != emp_id:
        return jsonify({'message': 'Cannot change emp_id'})
    
    curr_data = r_conn.get(employee_key)
    if  curr_data == None:
        return jsonify({'message': f'Employee with emp_id:{emp_id}, does not exists.'})
    
    curr_data_json = json.loads(r_conn.get(employee_key))
    if curr_data_json['email'] == data['email']:
        return jsonify({'message': f"Employee with email :{data['email']}, already exists."})

    r_conn.set(employee_key, (json.dumps(data)))
    return jsonify({'message': f'Emoloyee with id:{emp_id}, updated successfully'})
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500
    

@redis_api_bp.route('/delete/<int:emp_id>', methods=['DELETE'])
def delete_employee(emp_id):
    try:
        employee_key = f"employee/{emp_id}"
        if r_conn.get(employee_key) == None:
            return jsonify({'message': f'Employee with emp_id:{emp_id}, does not exists.'})
        r_conn.delete(employee_key)
        return jsonify({'message': f'Employee with emp_id:{emp_id}, deleted successfully'})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
