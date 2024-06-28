from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)

    from app.controllers.openai_controller import openai_bp
    app.register_blueprint(openai_bp, url_prefix='/openai')

    from app.controllers.rule_controller import rule_bp
    app.register_blueprint(rule_bp, url_prefix='/manual')
    
    from app.controllers.sparql_controller import sparql_bp
    app.register_blueprint(sparql_bp, url_prefix='/sparql')

    return app
