
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "local-development-only-change-before-deployment"
    )

    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" + os.path.join(BASE_DIR, "team_finder.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
