from flask import Blueprint, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models import db, Person, UserType
from app.swagger.guides import get_patient_desc, get_patients_desc
from flasgger import swag_from
from app import BLOCKLIST

patients = Blueprint("patients", __name__)
CORS(patients)  # Apply CORS to all routes within this Blueprint


@patients.route("/patients", methods=["GET"])
@jwt_required()
@swag_from(get_patients_desc)
def get_patients():
    """
    Get a list of patients with optional filters and pagination.
    """
    token = request.headers.get("Authorization").split(" ")[1]
    if token in BLOCKLIST:
        return jsonify({"error": "Permission denied"}), 401

    identity = get_jwt_identity()
    user = Person.query.filter_by(identifier_value=identity).first()
    if user.user_type == 2:
        return jsonify({"error": "Permission denied"}), 401

    # Query parameters
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("limit", 15))
    name = request.args.get("name")
    email = request.args.get("email")
    gender = request.args.get("gender")

    # Base query with patient type filter
    query = Person.query.join(UserType).filter(UserType.name == "patient")

    # Apply filters
    if name:
        query = query.filter(
            (Person.name_given.ilike(f"%{name}%"))
            | (Person.name_family.ilike(f"%{name}%"))
        )
    if email:
        query = query.filter(Person.identifier_value.ilike(f"%{email}%"))
    if gender:
        query = query.filter(Person.gender.ilike(gender))

    # Pagination using updated syntax
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    patients = pagination.items

    # Response
    response = {
        "total": pagination.total,
        "page": page,
        "limit": per_page,
        "data": [
            {
                "id": patient.id,
                "name_given": patient.name_given,
                "name_family": patient.name_family,
                "birth_date": patient.birth_date.isoformat(),
                "gender": patient.gender,
                "telecom": {
                    "system": patient.telecom_system,
                    "value": patient.telecom_value,
                },
                "active": patient.active,
            }
            for patient in patients
        ],
    }

    return jsonify(response), 200


@patients.route("/patients/<int:patient_id>", methods=["GET"])
@jwt_required()
@swag_from(get_patient_desc)
def get_patient(patient_id):
    """
    Get details of a specific patient by ID.
    """
    token = request.headers.get("Authorization").split(" ")[1]
    if token in BLOCKLIST:
        return jsonify({"error": "Permission denied"}), 401

    patient = Person.query.filter_by(id=patient_id, active=1).first()

    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    response = {
        "id": patient.id,
        "name": f"{patient.name_given} {patient.name_family}",
        "birth_date": patient.birth_date.isoformat(),
        "gender": patient.gender,
        "telecom": {
            "system": patient.telecom_system,
            "value": patient.telecom_value,
        },
        "active": patient.active,
    }
    return jsonify(response), 200
