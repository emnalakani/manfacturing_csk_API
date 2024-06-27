from flask import Blueprint, request, jsonify
from app.services.openai_service import ask_openai, load_context
from app.services.rule_service import MCSK, determine_rule_template, SpecializeRule, generate_sparql_query, generate_datalog_rule
import re

openai_bp = Blueprint('openai_bp', __name__)

@openai_bp.route('/generate_rule/openAI', methods=['POST'])
def generate_rule():
    data = request.json
    nl_input = data.get('nl_input')
    if not nl_input:
        return jsonify({"error": "Missing nl_input"}), 400

    messages = load_context()
    try:
        # Get response from OpenAI
        response = ask_openai(nl_input, messages)
        
        # Process the response to remove unwanted parts and split into statements
        processed_statements = process_response(response)

        # Print and process each statement individually
        rules = []
        sparql_queries = []
        datalog_rules = []
        for statement in processed_statements:
            print("Processing statement:", statement)  # Debug print each statement
            mcsk = MCSK(statement)
            rt = determine_rule_template(mcsk)
            concrete_rule = SpecializeRule(rt, mcsk)
            sparql_query = generate_sparql_query(concrete_rule)
            datalog_rule = generate_datalog_rule(concrete_rule)
            rules.append(str(concrete_rule))
            sparql_queries.append(sparql_query)
            datalog_rules.append(datalog_rule)

        return jsonify({"response": response, "rules": rules, "sparql_queries": sparql_queries, "datalog_rules": datalog_rules}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def process_response(response):
    """Cleans the response and splits it into individual statements."""
    clean_response = response.replace('Process Requirement:', '').replace('Tool Requirement:', '').strip()
    clean_response = re.sub(r'\d+\.\d+', '', clean_response)  # Remove enumeration like 1.1, 1.2, etc.
    statements = [line.strip() for line in clean_response.split('\n') if line.strip()]
    return statements
