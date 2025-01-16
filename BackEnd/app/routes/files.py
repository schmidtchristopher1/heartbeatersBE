from flask import Blueprint, current_app, json, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from werkzeug.utils import secure_filename
from app.swagger.guides import files_desc
from flasgger import swag_from
from app import BLOCKLIST
from datetime import datetime
from app.models import Person, db, FileMeta
from app.utilities.util import Util

files = Blueprint("files", __name__)
CORS(files)  # Apply CORS to all routes within this Blueprint

# Allowed extensions
ALLOWED_EXTENSIONS = {"json"}


# Helper function to validate file extensions
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@files.route("/upload", methods=["POST"])
@swag_from(files_desc)
@jwt_required()
def upload_file():
    try:
        token = request.headers.get("Authorization").split(" ")[1]
        if token in BLOCKLIST:
            return jsonify({"error": "Permission denied"}), 401

        current_user = get_jwt_identity()
        timestamp = datetime.now()

        file = request.files.get("file")
        if not file or not allowed_file(file.filename):
            return (
                jsonify({"error": "Invalid file type. Only .json files allowed."}),
                400,
            )

        # Get patient ID
        patient = Person.query.filter_by(identifier_value=current_user).first()
        if not patient:
            return jsonify({"error": "Patient not found"}), 404

        # Create secure filename with timestamp
        filename = secure_filename(file.filename)
        file_type = filename.rsplit(".", 1)[1].lower()

        # Save file
        file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)

        file_data = Util.extract_heart_rate_values(file_path)

        # Convert dictionary to JSON string
        hr_data_json = json.dumps(file_data)

        # Save metadata
        try:
            new_file = FileMeta(
                patient_id=patient.id,
                filename=filename,
                file_type=file_type,
                created_at=timestamp,
                hr_data=hr_data_json,  # Save as string
            )
            db.session.add(new_file)
            db.session.commit()
        except Exception as e:
            print(f"Error saving file metadata: {str(e)}")
            return jsonify({"error": "Error saving file metadata"}), 500

        return (
            jsonify(
                {
                    "message": "File uploaded successfully",
                    "file_id": new_file.id,
                    "filename": filename,
                    "created_at": timestamp.isoformat().replace("T", " ").split(".")[0],
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@files.route("/list-files", methods=["GET"])
@jwt_required()
def list_files():
    try:
        current_user = get_jwt_identity()
        patient = Person.query.filter_by(identifier_value=current_user).first()
        if not patient:
            return jsonify({"error": "Patient not found"}), 404

        # Join with Person to get uploader info
        files = (
            FileMeta.query.join(Person, FileMeta.patient_id == Person.id)
            .filter(FileMeta.patient_id == patient.id)
            .all()
        )

        if not files:
            return jsonify({"message": "No files found"}), 404

        file_list = []
        for file in files:
            uploader = Person.query.get(file.patient_id)
            file_list.append(
                {
                    "file_id": file.id,
                    "filename": file.filename,
                    "file_type": file.file_type,
                    "uploaded_by": f"{uploader.name_given} {uploader.name_family}",
                    "created_at": file.created_at.isoformat()
                    .replace("T", " ")
                    .split(".")[0],
                }
            )

        return jsonify({"files": file_list}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@files.route("/list-patient-files/<int:patient_id>", methods=["GET"])
@jwt_required()
def list_files_by_patient(patient_id):
    try:
        # Get current user and check if clinician
        current_user = get_jwt_identity()
        user = Person.query.filter_by(identifier_value=current_user).first()

        if user.user_type == 2:  # 2 is patient type
            return (
                jsonify(
                    {
                        "error": "Permission denied. Only clinicians can access this endpoint"
                    }
                ),
                403,
            )

        # Check if requested patient exists
        patient = Person.query.filter_by(id=patient_id).first()
        if not patient:
            return jsonify({"error": "Patient not found"}), 404

        # Get files using relationship
        files = FileMeta.query.filter_by(patient_id=patient_id).all()

        if not files:
            return jsonify({"message": "No files found"}), 404

        file_list = []
        for file_entry in files:
            file_list.append(
                {
                    "file_id": file_entry.id,
                    "filename": file_entry.filename,
                    "file_type": file_entry.file_type,
                    "uploaded_by": f"{file_entry.uploader.name_given} {file_entry.uploader.name_family}",
                    "created_at": file_entry.created_at.isoformat()
                    .replace("T", " ")
                    .split(".")[0],
                }
            )

        return jsonify({"files": file_list}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
