import os
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-key-before-deployment")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///farmer_crop.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
