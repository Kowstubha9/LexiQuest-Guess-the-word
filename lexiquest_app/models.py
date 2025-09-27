from lexiquest_app import db 
from datetime import datetime
from sqlalchemy.dialects.mysql import ENUM
from werkzeug.security import generate_password_hash, check_password_hash

# User Model
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(ENUM('player', 'admin'), nullable=False, default='player')
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)
    
    games = db.relationship('Game', backref='player', lazy='dynamic')
    
    # Method to hash the password
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    # Method to check the password
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    # Method to check role
    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'

# Word List Model 
class WordList(db.Model):
    __tablename__ = 'word_list'
    
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(5), unique=True, nullable=False) # 5-letter word

    def __repr__(self):
        return f'<WordList {self.word}>'

# Game Model (Tracks a single session/word attempt) 
class Game(db.Model):
    __tablename__ = 'games'
    
    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    target_word = db.Column(db.String(5), nullable=False) 
    date_played = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())
    
    status = db.Column(
        ENUM('win', 'loss', 'in_progress'), 
        nullable=False, 
        default='in_progress'
    )
    
    # Relationship to the Guesses model
    guesses = db.relationship('Guess', backref='game', lazy='dynamic')

    def __repr__(self):
        return f'<Game {self.id} | User {self.user_id} | Word {self.target_word} | Status {self.status}>'

# Guess Model (Tracks individual guesses within a game) 
class Guess(db.Model):
    __tablename__ = 'guesses'
    
    id = db.Column(db.Integer, primary_key=True)

    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    
    guess_word = db.Column(db.String(5), nullable=False)
    guess_number = db.Column(db.SmallInteger, nullable=False) 
    
    feedback_json = db.Column(db.String(512)) 

    __table_args__ = (
        db.UniqueConstraint('game_id', 'guess_number', name='unique_guess_per_game'),
    )

    def __repr__(self):
        return f'<Guess {self.guess_word} for Game {self.game_id}>'