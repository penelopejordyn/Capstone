from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class user(db.Model):
    """user model."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


def connect_db(app):
    """Connect to database."""
    db.app = app
    db.init_app(app)