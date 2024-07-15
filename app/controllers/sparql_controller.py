

from flask import Blueprint, jsonify, request

from app.services.sparql_service import add_classes_to_triple_store


sparql_bp = Blueprint('sparql_bp', __name__)


@sparql_bp.route('/add_classes', methods=['POST'])
def add_classes():
    try:
        data = request.get_json()
        expression = data.get('expression') 
        #query = data.get("query")

        if not expression:
            return jsonify({"error": "Expression not provided"}), 400
        #if not query:
        #    return jsonify({"error": "Query not provided"}), 400

        result_message = add_classes_to_triple_store(expression)

        return jsonify({"message": result_message}), 200

        if result_message == False:
            return jsonify({"error creating nw classes"}), 500
        else:
            result_message = execute_insert_sparql_query(query)
            if result_message == False:
                return jsonify({"error populatig kg"}), 500
            else:
                return jsonify({"message": result_message}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@sparql_bp.route('/add_multiple_classes', methods=['POST'])
def add_multiple_classes():
    try:
        data = request.get_json()
        expressions = data.get('expressions')  # Expecting 'expressions' to be a list

        if not expressions or not isinstance(expressions, list):
            return jsonify({"error": "A list of expressions not provided"}), 400

        results = []
        for expression in expressions:
            if not expression:
                results.append({"error": "Empty expression provided"})
                continue
            try:
                result_message = add_classes_to_triple_store(expression)
                results.append({"expression": expression, "message": result_message})
            except Exception as e:
                results.append({"expression": expression, "error": str(e)})

        return jsonify({"results": results}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500