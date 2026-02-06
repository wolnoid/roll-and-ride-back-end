from functools import wraps
from flask import request, jsonify, g
import jwt
import os

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.headers.get("Authorization")
        if not auth:
            return jsonify({"error": "Unauthorized"}), 401

        parts = auth.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({"error": "Authorization header must be: Bearer <token>"}), 401

        token = parts[1]

        try:
            decoded = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
            # Handle both formats:
            g.user = decoded.get("payload", decoded)

            if "id" not in g.user:
                return jsonify({"error": "Invalid token payload"}), 401

        except Exception as error:
            return jsonify({"error": str(error)}), 401

        return f(*args, **kwargs)
    return decorated_function