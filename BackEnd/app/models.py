from app import db
from sqlalchemy import CheckConstraint
from datetime import datetime


class UserType(db.Model):
    __tablename__ = "user_type"

    id = db.Column(db.Integer, primary_key=True)
    snomed_code = db.Column(db.String)
    name = db.Column(db.String, unique=True)

    __table_args__ = (
        CheckConstraint(
            name.in_(["practitioner", "patient", "radiologist", "cardiologist"]),
            name="check_user_type_name",
        ),
    )


class Person(db.Model):
    __tablename__ = "person"

    id = db.Column(db.Integer, primary_key=True)
    identifier_value = db.Column(db.Text, unique=True)
    name_family = db.Column(db.Text)
    name_given = db.Column(db.Text)
    birth_date = db.Column(db.Date)
    password_hash = db.Column(db.Text)
    telecom_system = db.Column(db.Text)
    telecom_value = db.Column(db.Text)
    gender = db.Column(db.Text)
    active = db.Column(db.Integer)
    user_type = db.Column(db.Integer, db.ForeignKey("user_type.id"))


class Auth(db.Model):
    __tablename__ = "auth"

    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey("person.id"))
    password = db.Column(db.Text)
    role = db.Column(db.Text)


class RegisterMeta(db.Model):
    __tablename__ = "register_meta"

    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey("person.id"))
    auth_id = db.Column(db.Integer, db.ForeignKey("auth.id"))
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class Qualification(db.Model):
    __tablename__ = "qualification"

    id = db.Column(db.Integer, primary_key=True)
    practitioner_id = db.Column(
        db.Integer, db.ForeignKey("person.id", ondelete="CASCADE")
    )
    qualification_code_text = db.Column(db.Text)


class FileMeta(db.Model):
    __tablename__ = "file_meta"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("person.id"))
    filename = db.Column(db.String(255))
    file_type = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    hr_data = db.Column(db.Text)

    uploader = db.relationship(
        "Person", backref="uploaded_files", foreign_keys=[patient_id]
    )
