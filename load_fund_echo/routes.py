from flask import request, jsonify, Blueprint
from query import load_echo_fund

api_bp = Blueprint('api_bp', __name__)

@api_bp.route('/loadEchoFund', methods=['POST'])
def create_update_record():
    data = request.get_json()

    responses = load_echo_fund(data)

    return jsonify({'status': 'success', 
                    'message': 'Records processed successfully', 'details': responses}), 200
