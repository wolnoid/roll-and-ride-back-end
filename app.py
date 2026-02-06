from flask import Flask
from dotenv import load_dotenv
from flask_cors import CORS
from auth_blueprint import authentication_blueprint
from hoots_blueprint import hoots_blueprint
from comments_blueprint import comments_blueprint

load_dotenv()

app = Flask(__name__)

CORS(
    app,
    resources={r"/*": {"origins": ["http://127.0.0.1:5173", "http://localhost:5173"]}},
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
)

app.register_blueprint(authentication_blueprint)
app.register_blueprint(hoots_blueprint)
app.register_blueprint(comments_blueprint)

app.run()