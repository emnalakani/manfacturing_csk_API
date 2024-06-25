from flask import Flask, request, jsonify
from flask_cors import CORS
from function import generate_concrete_rule, generate_sparql_query, generate_datalog_rule

# Define the MCSK class if not imported from function.py
class MCSK:
    def __init__(self, statement: str):
        self.statement = statement

    def __str__(self):
        return self.statement

app = Flask(__name__)
CORS(app)

@app.route('/generate_rule', methods=['POST'])
def generate_rule():
    data = request.json
    nl_input = data.get('nl_input')

    if not nl_input:
        return jsonify({"error": "Missing nl_input"}), 400

    try:
        concrete_rule = generate_concrete_rule(nl_input)
        return jsonify({"concrete_rule": str(concrete_rule)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return 'Hello, this is server for Cheikmat project'

@app.route('/generate', methods=['POST'])
def generateCS():
    data = request.get_json()
    mcsk_inputs = data.get('mcsk_inputs')

    print(mcsk_inputs)

    generated_concrete_rules = []
    generated_sparql_queries = []
    generated_datalog_rules = []

    for mcsk_input in mcsk_inputs:
        try:
            mcsk = MCSK(mcsk_input)
            cr = generate_concrete_rule(mcsk_input)
            print(f"Generated Concrete Rule for '{mcsk_input}': {cr}")
            generated_concrete_rules.append(cr.expression)

            sparql_query = generate_sparql_query(cr)
            print(f"Generated SPARQL Query for '{mcsk_input}':\n{sparql_query}")
            generated_sparql_queries.append(sparql_query)

            datalog_rule = generate_datalog_rule(cr)
            print(f"Generated Datalog Rule for '{mcsk_input}':\n{datalog_rule}")
            generated_datalog_rules.append(datalog_rule)

        except ValueError as e:
            print(f"Failed to generate rule for '{mcsk_input}': {e}")
    
    return jsonify({
        'generated_concrete_rules': generated_concrete_rules,
        'generated_sparql_queries': generated_sparql_queries,
        'generated_datalog_rules': generated_datalog_rules
    })

if __name__ == '__main__':
    app.run(debug=True)
