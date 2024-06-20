import json
import redis
from os import getenv
from flask import jsonify, Blueprint, request, current_app as app
from config import get_configs

# Define a Blueprint for the Redis API routes
redis_api_bp = Blueprint('redis_api', __name__)
print('-----------------------PRODUCER-----------------')


def create_redis_connection():
    """
    Create a connection to the Redis server using configuration from the Flask app.
    """
    configs = get_configs(app)
    REDIS_HOST = configs.get('REDIS_HOST', 'redis-container')
    REDIS_PORT = int(configs.get('REDIS_PORT', 6379))
    
     # Establish connection to Redis
    r_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    return r_conn


# Create a Redis connection
r_conn = create_redis_connection()


@redis_api_bp.route('/create', methods=['POST'])
def create_employee(): 
    """
    Create a new employee entry in Redis.
    """ 
    data = request.get_json()
    try:
        employee_key = f"employee/{data['emp_id']}"

        # Check if employee already exists
        if r_conn.get(employee_key) != None:
            return jsonify({'message': f"Employee with emp_id: {data['emp_id']} already exists."}), 409
        
        # Create a new employee
        r_conn.set(employee_key, (json.dumps(data)))
        return jsonify({'message': 'Employee created successfully'}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@redis_api_bp.route('/update/<int:emp_id>', methods=['PUT'])
def update_employee(emp_id):
    """
    Update an existing employee entry in Redis.
    """
    data = request.get_json()
    try:
        employee_key = f"employee/{emp_id}"

        # Check if employee exists
        curr_data = r_conn.get(employee_key)
        if  curr_data == None:
            return jsonify({'message': f'Employee with emp_id:{emp_id}, does not exists.'}), 404
        
        # Ensure emp_id cannot be changed
        if data['emp_id'] != emp_id:
            return jsonify({'message': "Cannot change emp_id"}), 400
        
        curr_data_json = json.loads(r_conn.get(employee_key))

        # Ensure email cannot be changed
        if curr_data_json['email'] != data['email']:
            return jsonify({'message': "Cannot change email"}), 400 
        
        # Check if any fields other than emp_id have changed
        is_changed = any(curr_data_json.get(field) != data.get(field) for field in data if field != 'emp_id')
        if not is_changed:
            return jsonify({'message': 'No changes detected'}), 200

        # Update the employee entry
        r_conn.set(employee_key, (json.dumps(data)))
        return jsonify({'message': f'Emoloyee with id:{emp_id}, updated successfully'}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@redis_api_bp.route('/delete/<int:emp_id>', methods=['DELETE'])
def delete_employee(emp_id):
    """
    Delete an existing employee entry in Redis.
    """
    try:
        employee_key = f"employee/{emp_id}"

        # Check if employee exists
        if r_conn.get(employee_key) == None:
            return jsonify({'message': f'Employee with emp_id:{emp_id}, does not exists.'}), 404
        
        # Delete the employee entry
        r_conn.delete(employee_key)
        return jsonify({'message': f'Employee with emp_id:{emp_id}, deleted successfully'}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
