from app import create_app, db
from app.models import UserType


class InitDB:

    @staticmethod
    def create_db():
        db.create_all()
        print("Database created successfully!")

    @staticmethod
    def flush_db():
        db.drop_all()
        db.create_all()
        print("Database flushed successfully!")

    @staticmethod
    def seed_db():
        """Seeds the database with initial data."""
        user_types = [
            UserType(name="practitioner", snomed_code="158965000"),
            UserType(name="patient", snomed_code="116154003"),
            UserType(name="radiologist", snomed_code="66862007"),
            UserType(name="cardiologist", snomed_code="17561000"),
        ]

        try:
            with db.session.begin():
                db.session.bulk_save_objects(user_types)
            print("Sample data inserted successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error inserting sample data: {e}")
        finally:
            db.session.close()


if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        InitDB.flush_db()
        InitDB.seed_db()
