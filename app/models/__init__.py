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
    sessions = db.relationship('ProblemSession', backref='user', lazy=True)

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


class Problem(db.Model):
    __tablename__ = 'problems'

    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50), nullable=False)
    external_id = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    title_slug = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    examples = db.Column(db.JSON)
    constraints = db.Column(db.JSON)
    difficulty = db.Column(db.String(20))
    tags = db.Column(db.JSON)
    created_at = db.Column(db.DateTime,
                 default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    __table_args__ = (
        db.UniqueConstraint('platform', 'external_id', name='unique_platform_problem'),
    )

    sessions = db.relationship('ProblemSession', backref='problem', lazy=True)

    def __repr__(self):
        return f'<Problem {self.platform}:{self.title}>'


class ProblemSession(db.Model):
    __tablename__ = 'problem_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id'), nullable=False)
    status = db.Column(db.String(20), default='in_progress')
    started_at = db.Column(db.DateTime,
                 default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    completed_at = db.Column(db.DateTime, nullable=True)

    attempts = db.relationship('Attempt', backref='session', lazy=True)

    def __repr__(self):
        return f'<ProblemSession user={self.user_id} problem={self.problem_id}>'


class Attempt(db.Model):
    __tablename__ = 'attempts'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('problem_sessions.id'), nullable=False)
    code = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(20), nullable=False)
    platform_verdict = db.Column(db.String(50))
    attempt_number = db.Column(db.Integer, nullable=False)
    submitted_at = db.Column(db.DateTime,
                  default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    review = db.relationship('Review', backref='attempt', lazy=True, uselist=False)

    def __repr__(self):
        return f'<Attempt {self.attempt_number} session={self.session_id}>'


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('attempts.id'), nullable=False)
    summary = db.Column(db.Text)
    correct = db.Column(db.JSON)
    issues = db.Column(db.JSON)
    complexity_time = db.Column(db.String(50))
    complexity_space = db.Column(db.String(50))
    think_about_this = db.Column(db.Text)
    hints = db.Column(db.JSON)
    vs_previous = db.Column(db.JSON)
    status = db.Column(db.String(20), default='needs work')
    hint_level_unlocked = db.Column(db.Integer, default=0)
    solution_revealed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime,
                 default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    def __repr__(self):
        return f'<Review attempt={self.attempt_id}>'