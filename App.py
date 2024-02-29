from flask import Flask, request, jsonify
from function import generate_concrete_rule

from function import generate_sparql_query
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This enables CORS for all routes

@app.route('/generate_rule', methods=['POST'])
def generate_rule():
    # Extract the natural language input from the request
    data = request.json
    nl_input = data.get('nl_input')

    if not nl_input:
        return jsonify({"error": "Missing nl_input"}), 400

    try:
        # Generate the concrete rule
        concrete_rule = generate_concrete_rule(nl_input)
        return jsonify({"concrete_rule": str(concrete_rule)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return 'Hello, this is server for CHeikmat project'


@app.route('/generate', methods=['POST'])
def generateCS():
    data = request.get_json()
    mcsk_inputs = data.get('mcsk_inputs')

    print(mcsk_inputs)

    generated_concerete_rule = []
    generated_sparql_query = []

    for mcsk_input in mcsk_inputs:
        try:
            cr = generate_concrete_rule(mcsk_input)
            print(f"Generated Concrete Rule for '{mcsk_input}': {cr}")
            generated_concerete_rule.append(cr.expression)

            sparql_query = generate_sparql_query(cr)
            print(f"Generated SPARQL Query for '{mcsk_input}':\n{sparql_query}")
            generated_sparql_query.append(sparql_query)

        except ValueError as e:
            print(f"Failed to generate rule for '{mcsk_input}': {e}")
    
    return jsonify({
        'generated_concerete_rule': generated_concerete_rule,
        'generated_sparql_query': generated_sparql_query
    })


if __name__ == '__main__':
    app.run(debug=True)
