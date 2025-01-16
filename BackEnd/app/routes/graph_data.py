from flask import Blueprint, json, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import BLOCKLIST
from app.utilities.util import Util
import os
from app.models import Person, FileMeta

graph_data = Blueprint("graph_data", __name__)
CORS(graph_data)

UPLOADS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads"
)


@graph_data.route("/heart-rate-data", methods=["GET"])
@jwt_required()
def get_heart_rate_data():
    try:
        # Get file ID from query parameters instead of JSON body
        file_id = request.args.get("file_id")
        if not file_id:
            return jsonify({"error": "File ID is required"}), 400

        # Convert file_id to integer
        try:
            file_id = int(file_id)
        except ValueError:
            return jsonify({"error": "Invalid file ID format"}), 400

        # Get current user's ID
        current_user = get_jwt_identity()
        user = Person.query.filter_by(identifier_value=current_user).first()

        # Get file metadata with proper parameter binding
        file_meta = FileMeta.query.filter_by(id=file_id, patient_id=user.id).first()

        return jsonify({"data": json.loads(file_meta.hr_data)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@graph_data.route("/heart-rate-data-clinician", methods=["POST"])
@jwt_required()
def get_heart_rate_data_clinician():
    try:
        # Verify current user and clinician status
        current_user = get_jwt_identity()
        user = Person.query.filter_by(identifier_value=current_user).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        if user.user_type == 2:
            return (
                jsonify(
                    {
                        "error": "Permission denied. Only clinicians can access this endpoint"
                    }
                ),
                403,
            )

        # Validate request data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        file_id = data.get("file_id")
        patient_id = data.get("patient_id")

        if not file_id:
            return jsonify({"error": "File ID is required"}), 400
        if not patient_id:
            return jsonify({"error": "Patient ID is required"}), 400

        # Validate file_id format
        try:
            file_id = int(file_id)
            patient_id = int(patient_id)
        except ValueError:
            return jsonify({"error": "Invalid ID format"}), 400

        # Check if patient exists
        patient = Person.query.filter_by(id=patient_id).first()
        if not patient:
            return jsonify({"error": "Patient not found"}), 404

        # Check if file exists for patient
        file_meta = FileMeta.query.filter_by(id=file_id, patient_id=patient_id).first()
        if not file_meta:
            return jsonify({"error": "File not found for this patient"}), 404

        # Return heart rate data
        return (
            jsonify(
                {
                    "patient_name": f"{patient.name_given} {patient.name_family}",
                    "data": json.loads(file_meta.hr_data),
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
