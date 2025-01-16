from os import environ, path
from dotenv import load_dotenv
import os

# Load environment variables from .env file
basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))


class Config:
    """Base configuration with common settings."""

    SECRET_KEY = environ.get("SECRET_KEY")
    STATIC_FOLDER = "static"
    TEMPLATES_FOLDER = "templates"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER")

class DevelopmentConfig(Config):
    """Development-specific configuration."""

    FLASK_ENV = "development"

    SQLALCHEMY_DATABASE_FILE_NAME = environ.get(
        "DEV_DB_NAME", "development.db"
    )
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, SQLALCHEMY_DATABASE_FILE_NAME)}"


class ProductionConfig(Config):
    """Production-specific configuration."""

    FLASK_ENV = "production"

    # Use a production database URI if provided
    SQLALCHEMY_DATABASE_FILE_NAME = environ.get(
        "PROD_DB_NAME", "production.db"
    )
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, SQLALCHEMY_DATABASE_FILE_NAME)}"

