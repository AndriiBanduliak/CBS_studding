from datetime import datetime
import jwt
from time import time
import os
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from blackjack import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(128))
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # User profile
    avatar = db.Column(db.String(120), default='default.png')
    
    # Game statistics
    games_played = db.Column(db.Integer, default=0)
    games_won = db.Column(db.Integer, default=0)
    games_lost = db.Column(db.Integer, default=0)
    games_tied = db.Column(db.Integer, default=0)
    biggest_win = db.Column(db.Integer, default=0)
    currency_balance = db.Column(db.Integer, default=1000)  # Starting balance
    
    # Relationships
    game_history = db.relationship('GameHistory', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def win_loss_ratio(self):
        if self.games_lost == 0:
            return self.games_won if self.games_won > 0 else 0
        return round(self.games_won / self.games_lost, 2)
    
    def get_verification_token(self, expires_in=3600):
        """Generate an email verification token for the user."""
        secret_key = os.environ.get('SECRET_KEY', 'dev')
        return jwt.encode(
            {'verify_email': self.id, 'exp': time() + expires_in},
            secret_key,
            algorithm='HS256'
        )
    
    def get_reset_password_token(self, expires_in=3600):
        """Generate a password reset token for the user."""
        secret_key = os.environ.get('SECRET_KEY', 'dev')
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            secret_key,
            algorithm='HS256'
        )
    
    @staticmethod
    def verify_token(token):
        """Verify email verification token."""
        secret_key = os.environ.get('SECRET_KEY', 'dev')
        try:
            id = jwt.decode(token, secret_key, algorithms=['HS256'])['verify_email']
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        return User.query.get(id)
    
    @staticmethod
    def verify_reset_password_token(token):
        """Verify password reset token."""
        secret_key = os.environ.get('SECRET_KEY', 'dev')
        try:
            id = jwt.decode(token, secret_key, algorithms=['HS256'])['reset_password']
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        return User.query.get(id)
        
    def __repr__(self):
        return f'<User {self.email}>'

class GameHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    player_hand = db.Column(db.String(64))  # Serialized cards
    dealer_hand = db.Column(db.String(64))  # Serialized cards
    bet_amount = db.Column(db.Integer)
    result = db.Column(db.String(20))  # 'win', 'loss', 'tie', 'blackjack'
    profit_loss = db.Column(db.Integer)  # Positive for win, negative for loss
    played_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Game {self.id} - {self.result}>'