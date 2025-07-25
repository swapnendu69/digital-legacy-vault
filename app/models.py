from . import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    vaults = db.relationship('Vault', backref='owner', lazy=True)
    successors = db.relationship('Successor', backref='user', lazy=True)

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    # The following methods are required by Flask-Login
    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return True

    def is_active(self):
        """True, as all users are active."""
        return True

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return str(self.id)

    def __repr__(self):
        return f'<User {self.email}>'


class Vault(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    data = db.Column(db.Text, nullable=False)  # Encrypted data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Vault {self.name}>'


class Successor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    relationship = db.Column(db.String(100))
    is_activated = db.Column(db.Boolean, default=False)
    activation_date = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Successor {self.name} ({self.email})>'