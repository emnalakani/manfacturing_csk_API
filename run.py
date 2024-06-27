# run.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

app = create_app()

# Print all registered routes
with app.app_context():
    print(app.url_map)

if __name__ == '__main__':
    app.run(debug=True)
