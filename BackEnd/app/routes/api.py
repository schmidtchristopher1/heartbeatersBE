# app/routes/api.py

from flask import Blueprint, jsonify
from flasgger import swag_from
from flask_cors import CORS
from app.swagger.guides import status_desc

api = Blueprint("api", __name__)
CORS(api)  # Apply CORS to all routes within this Blueprint


@api.route("/status")
@swag_from(status_desc)
def status():
    """Endpoint to get application status
    ---
    tags:
      - Status
    responses:
      200:
        description: Returns the status of the app
    """
    return jsonify({"status": "OK"})
