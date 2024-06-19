import json
import redis
from os import getenv
from flask import jsonify, Blueprint, request, current_app as app
from config import get_configs

redis_api_bp = Blueprint('redis_api', __name__)
print('-----------------------PRODUCER-----------------')


def create_redis_connection():
    configs = get_configs(app)
    REDIS_HOST = configs.get('REDIS_HOST', 'redis-container')
    REDIS_PORT = int(configs.get('REDIS_PORT', 6379))

    r_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    return r_conn


r_conn = create_redis_connection()


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
        return jsonify({'message': "Cannot change emp_id"})
    
    curr_data = r_conn.get(employee_key)
    if  curr_data == None:
        return jsonify({'message': f'Employee with emp_id:{emp_id}, does not exists.'})
    
    curr_data_json = json.loads(r_conn.get(employee_key))
    if curr_data_json['email'] != data['email']:
        return jsonify({'message': "Cannot change email"})

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
    
