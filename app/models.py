
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import UniqueConstraint
from app import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    education = db.Column(db.String(150), default="")
    skills = db.Column(db.Text, default="")
    interests = db.Column(db.Text, default="")
    preferred_role = db.Column(db.String(100), default="")
    experience = db.Column(db.String(50), default="Beginner")
    availability = db.Column(db.String(100), default="Flexible")
    goals = db.Column(db.Text, default="")
    work_preference = db.Column(db.String(100), default="Remote")
    bio = db.Column(db.Text, default="")

    projects = db.relationship("Project", backref="creator", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    required_skills = db.Column(db.Text, default="")
    roles_needed = db.Column(db.Text, default="")
    interests = db.Column(db.Text, default="")
    experience = db.Column(db.String(50), default="Beginner")
    availability = db.Column(db.String(100), default="Flexible")
    goals = db.Column(db.Text, default="")
    work_preference = db.Column(db.String(100), default="Remote")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


class JoinRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )
    project_id = db.Column(
        db.Integer, db.ForeignKey("project.id"), nullable=False
    )

    status = db.Column(db.String(20), default="Pending", nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    __table_args__ = (
        UniqueConstraint(
            "user_id", "project_id",
            name="unique_user_project_request"
        ),
    )


class TeamMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )
    project_id = db.Column(
        db.Integer, db.ForeignKey("project.id"), nullable=False
    )

    role = db.Column(db.String(100), default="Member")
    joined_at = db.Column(db.DateTime, server_default=db.func.now())

    __table_args__ = (
        UniqueConstraint(
            "user_id", "project_id",
            name="unique_team_member"
        ),
    )


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )

    message = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(255), default="")
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship("User", backref=db.backref(
        "notifications", lazy=True, cascade="all, delete-orphan"
    ))
