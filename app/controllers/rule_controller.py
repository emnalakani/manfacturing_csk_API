from flask import Blueprint, request, jsonify
from app.services.rule_service import generate_concrete_rule, generate_sparql_query, generate_datalog_rule

rule_bp = Blueprint('rule_bp', __name__)

@rule_bp.route('/generate_rule', methods=['POST'])
def generate_rule():
    data = request.json
    nl_input = data.get('nl_input')

    if not nl_input:
        return jsonify({"error": "Missing nl_input"}), 400

    try:
        concrete_rule = generate_concrete_rule(nl_input)
        sparql_query = generate_sparql_query(concrete_rule)
        datalog_rule = generate_datalog_rule(concrete_rule)
        return jsonify({
            "concrete_rule": str(concrete_rule),
            "sparql_query": sparql_query,
            "datalog_rule": datalog_rule
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@rule_bp.route('/')
def index():
    return 'Hello, this is server for Cheikmat project'
