from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, 
                 default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    coding_profiles = db.relationship('CodingProfile', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'


class CodingProfile(db.Model):
    __tablename__ = 'coding_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    platform_username = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime,
                 default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    def __repr__(self):
        return f'<CodingProfile {self.platform}:{self.platform_username}>'