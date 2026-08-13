from flask import Flask
from flask_cors import CORS

from backend.routes import routes

app = Flask(__name__)

CORS(app)

app.register_blueprint(routes)


@app.route("/")
def home():
    return {
        "message": "TruthLens AI Backend is running",
        "status": "success"
    }


if __name__ == "__main__":
    app.run(debug=True)