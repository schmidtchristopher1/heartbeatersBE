from flask import Blueprint, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import (
    db,
    Person,
    UserType,
    RegisterMeta,
    Auth,
)
from app.swagger.guides import register_desc, login_desc
from flasgger import swag_from
from app.utilities.util import Util
from datetime import datetime, timedelta
from app import BLOCKLIST

auth = Blueprint("auth", __name__)
CORS(auth)  # Apply CORS to all routes within this Blueprint


@auth.route("/register/patient", methods=["POST"])
@swag_from(register_desc)
def register_person():
    """
    Registration endpoint for generic person users (e.g., patients).
    """
    data = request.get_json()
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    password = data.get("password")
    gender = data.get("gender")
    date_of_birth = data.get("dob")
    user_type = UserType.query.filter_by(name="patient").first()

    # Validate input
    if not first_name:
        return jsonify({"error": "First name is required"}), 400
    if not last_name:
        return jsonify({"error": "Last name is required"}), 400
    if not email:
        return jsonify({"error": "Email is required"}), 400
    if not password:
        return jsonify({"error": "Password is required"}), 400
    if not date_of_birth:
        return jsonify({"error": "Date of birth is required"}), 400
    if not Util.check_email_address(email):
        return jsonify({"error": "Invalid email address"}), 400

    # Check for existing user
    existing_person = Person.query.filter_by(identifier_value=email).first()
    if existing_person:
        return jsonify({"error": "Email already registered"}), 400

    # Hash the password
    hashed_password = generate_password_hash(password)

    # Convert string date to Python date object
    try:
        birth_date = datetime.strptime(date_of_birth, "%m/%d/%Y").date()
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid date format. Use MM/DD/YYYY"}), 400

    # Create a new person
    try:
        new_person = Person(
            identifier_value=email,
            name_given=first_name,
            name_family=last_name,
            password_hash=hashed_password,
            telecom_system="email",
            telecom_value=email,
            birth_date=birth_date,  # Use converted date object
            gender=gender,
            active=0,
            user_type=user_type.id,
        )
        db.session.add(new_person)
        db.session.commit()

        new_auth = Auth(
            person_id=new_person.id,
            password=hashed_password,
            role="patient",
        )
        db.session.add(new_auth)
        db.session.commit()

        new_register_meta = RegisterMeta(
            person_id=new_person.id,
            auth_id=new_auth.id,
        )
        db.session.add(new_register_meta)
        db.session.commit()

        return jsonify({"message": "Person registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@auth.route("/register/clinician", methods=["POST"])
@swag_from(register_desc)
def register_clinician():
    """
    Registration endpoint for clinician users.
    """
    data = request.get_json()
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    password = data.get("password")
    type = data.get("type")
    user_type = UserType.query.filter_by(snomed_code=type).first()

    # Check if the user type exists
    if not user_type:
        return jsonify({"error": "Invalid clinician type"}), 400

    # Validate input
    if not first_name:
        return jsonify({"error": "First name is required"}), 400
    if not last_name:
        return jsonify({"error": "Last name is required"}), 400
    if not email:
        return jsonify({"error": "Email is required"}), 400
    if not password:
        return jsonify({"error": "Password is required"}), 400
    if not user_type:
        return jsonify({"error": "Clinician Type is required"}), 400

    # Check for existing user
    existing_person = Person.query.filter_by(identifier_value=email).first()
    if existing_person:
        return jsonify({"error": "Email already registered"}), 400

    # Hash the password
    hashed_password = generate_password_hash(password)

    # Create a new person
    try:
        new_person = Person(
            identifier_value=email,
            name_given=first_name,
            name_family=last_name,
            password_hash=hashed_password,
            telecom_system="email",
            telecom_value=email,
            active=0,
            user_type=user_type.id,
        )
        db.session.add(new_person)
        db.session.commit()

        new_auth = Auth(
            person_id=new_person.id,
            password=hashed_password,
            role="clinician",
        )
        db.session.add(new_auth)
        db.session.commit()

        new_register_meta = RegisterMeta(
            person_id=new_person.id,
            auth_id=new_auth.id,
        )
        db.session.add(new_register_meta)
        db.session.commit()

        return jsonify({"message": "Clinician registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@auth.route("/login", methods=["POST"])
@swag_from(login_desc)
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    # Validate input
    if not email:
        return jsonify({"error": "Email is required"}), 400
    if not password:
        return jsonify({"error": "Password is required"}), 400

    # Query the person table to find the user
    user = Person.query.filter_by(identifier_value=email).first()
    if not user:
        return jsonify({"error": "Unknown email address"}), 401

    # Query to check user type
    user_type = Person.query.filter_by(identifier_value=email).first().user_type
    if user_type == 2:
        user_type = "patient"
    else:
        user_type = "clinician"

    print(f"User type: {user_type}")

    # Verify password
    if not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid password"}), 401

    # Query the active status us user
    user = Person.query.filter_by(identifier_value=email).first()
    if user.active == 1:
        return jsonify({"error": "User already logged in"}), 401

    try:
        # Update active status to true
        user.active = 1
        db.session.commit()

        # Generate an access token for the user
        access_token = create_access_token(
            identity=email, expires_delta=timedelta(hours=3)
        )  # 3 hour expiration time
        return (
            jsonify(
                {
                    "access_token": access_token,
                    "first_name": user.name_given,
                    "last_name": user.name_family,
                    "user_type": user_type,
                }
            ),
            200,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@auth.route("/logout", methods=["POST"])
@swag_from("")
@jwt_required()
def logout():
    user = get_jwt_identity()

    # Query and change active status to false
    person = Person.query.filter_by(identifier_value=user).first()
    if person.active == 0:
        return jsonify({"error": "User already logged out"}), 401
    else:
        person.active = 0
        db.session.commit()

    token = request.headers.get("Authorization").split(" ")[1]
    BLOCKLIST.add(token)
    return jsonify({"message": "Successfully logged out"}), 200
