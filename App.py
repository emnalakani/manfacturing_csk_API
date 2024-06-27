from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)

    from app.controllers.openai_controller import openai_bp
    app.register_blueprint(openai_bp, url_prefix='')

    return app
