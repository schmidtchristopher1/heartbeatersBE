from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
from dotenv import load_dotenv
from pathlib import Path
from os import environ
from app.config import Config
import os

# Load environment variables from .env file
dotenv_path = Path(".env")
load_dotenv(dotenv_path)

# Initialize database
db = SQLAlchemy()

# Initialize blocklist set for storing JWT tokens
BLOCKLIST = set()


# Create the Flask application
def create_app(config_class=None):
    app = Flask(__name__)

    # Configure app based on environment
    if config_class:
        app.config.from_object(config_class)
    elif os.getenv("FLASK_ENV") == "development":
        from app.config import DevelopmentConfig

        app.config.from_object(DevelopmentConfig)
    else:
        from app.config import ProductionConfig

        app.config.from_object(ProductionConfig)

    # Set additional configuration
    app.config["SECRET_KEY"] = environ.get("SECRET_KEY")
    app.config["JWT_SECRET_KEY"] = environ.get("JWT_SECRET_KEY")
    app.config.setdefault("ENV", os.getenv("FLASK_ENV", "development"))

    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)

    # Initialize Swagger with custom configuration
    swagger = Swagger(
        app,
        template={
            "info": {
                "title": "My Flask API",
                "description": "This is a simple Flask API.",
                "version": "1.0.0",
            },
            "host": (
                "localhost:5000"
                if app.config["ENV"] == "development"
                else "your-production-host"
            ),
        },
    )
    # Create upload folder if not exists 
    UPLOAD_DIR: str = Config.UPLOAD_FOLDER
    if not os.path.exists(UPLOAD_DIR): 
        print(f"Creating folder for uploads: {UPLOAD_DIR}.")
        os.makedirs(UPLOAD_DIR)

    # Register blueprints
    from app.routes.main import main
    from app.routes.api import api
    from app.routes.auth import auth
    from app.routes.files import files
    from app.routes.patient import patients
    from app.routes.graph_data import graph_data

    app.register_blueprint(main)
    app.register_blueprint(api)
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(files)
    app.register_blueprint(patients)
    app.register_blueprint(graph_data)

    # Environment-specific database handling
    with app.app_context():
        from app.init_db import InitDB

        db_file: str = app.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///", "")

        if not os.path.exists(db_file):
            print("Database not found. Initializing production database...")
            db.create_all()
            InitDB.seed_db()

        if app.config["ENV"] == "development":
            print("Flushing and seeding the database for development...")
            InitDB.flush_db()
            InitDB.seed_db()
        elif app.config["ENV"] == "production":
            print(f"Environment : {app.config['ENV']}. Continue...")
        else:
            raise NotImplementedError("Missing information about variable - FLASK_ENV")

    return app

# Expose the app callable for Gunicorn
app = create_app()
