import os
from dotenv import load_dotenv

# Load environment variables from .env file (remember to create a .env file in the root of the project)
load_dotenv()


class Config(object):
    """
    Common configurations
    """

    TESTING = False


class ProductionConfig(Config):
    """
    Production configurations
    """

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SECRET_KEY = os.environ.get("BCRYPT_SECRET_KEY")
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "pool_recycle": 60,
        "pool_pre_ping": True,
    }
    #GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
    #GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")


class DevelopmentConfig(Config):
    """
    Development configurations
    """

    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = f"postgresql://{os.getenv("DB_USER")}:{os.getenv(
        "DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}"
    #GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    #GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")


class TestingConfig(Config):
    """
    Testing configurations
    """

    TESTING = True


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}