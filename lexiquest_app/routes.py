from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
from lexiquest_app import db
from lexiquest_app.models import User, WordList, Game, Guess
from lexiquest_app.utils import is_valid_username, is_valid_password, calculate_guess_feedback
from lexiquest_app.config import Config
from sqlalchemy.exc import IntegrityError
from datetime import date
import random
import json

bp = Blueprint('main', __name__)

# Helper Functions 

def login_required(f):
    """Decorator to check if a user is logged in."""
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
                 return jsonify({'message': 'Unauthorized access. Please log in.'}), 401
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

def admin_required(f):
    """Decorator to check if the logged-in user is an admin."""
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'message': 'Unauthorized access. Please log in.'}), 401
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            return jsonify({'message': 'Access denied. Admin privileges required.'}), 403
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

def check_daily_limit(f):
    """Decorator to enforce the max 3 games per user per day limit."""
    @login_required
    def wrapper(*args, **kwargs):
        user_id = session['user_id']
        today = date.today()
        
        games_played_today = Game.query.filter(
            Game.user_id == user_id,
            Game.date_played == today
        ).count()
        
        if games_played_today >= Config.MAX_WORDS_PER_DAY:
            return jsonify({
                'message': f"You have reached your daily limit of {Config.MAX_WORDS_PER_DAY} words. Better luck tomorrow!"
            }), 403
            
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# Root Route (Landing Page)
@bp.route('/', methods=['GET'])
def index():
    """Renders the welcome/login/registration page."""
    if 'user_id' in session:
        if session['role'] == 'admin':
            return redirect(url_for('main.admin_dashboard'))
        return redirect(url_for('main.game_page'))
        
    return render_template('index.html', message="Welcome to LexiQuest!")

# Player Game Page
@bp.route('/game', methods=['GET'])
@login_required
def game_page():
    """Renders the main game interface."""
    if session['role'] == 'admin':
        return redirect(url_for('main.admin_dashboard'))
    return render_template('game.html')

# Admin Dashboard Page
@bp.route('/admin', methods=['GET'])
@admin_required
def admin_dashboard():
    """Renders the admin dashboard."""
    return render_template('admin.html')

# User Authentication API Routes 
# Registration Route
@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # Validation Checks
    if not username or not password:
        return jsonify({'message': 'Username and password are required.'}), 400

    if not is_valid_username(username):
        return jsonify({'message': f'Username must be at least {Config.MIN_USERNAME_LENGTH} letters.'}), 400
        
    if not is_valid_password(password):
        return jsonify({
            'message': 'Password is too weak. It must be at least 5 characters, contain letters, numbers, and one of: $, %, *, @.'
        }), 400

    # Check for existing user
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists.'}), 409

    # Create and save new user (default role is 'player')
    try:
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'Registration successful. Please log in.'}), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Database error: Could not register user.'}), 500


# Login Route
@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user is None or not user.check_password(password):
        return jsonify({'message': 'Invalid username or password.'}), 401

    session['user_id'] = user.id
    session['username'] = user.username
    session['role'] = user.role

    if user.is_admin():
        redirect_url = url_for('main.admin_dashboard')
    else:
        redirect_url = url_for('main.game_page')

    return jsonify({
        'message': 'Login successful.',
        'username': user.username,
        'role': user.role,
        'redirect_url': redirect_url
    }), 200


# Logout Route
@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    return jsonify({'message': 'Logged out successfully.'}), 200

# Game API Routes 
# Start Game Route
@bp.route('/api/game/start', methods=['POST'])
@check_daily_limit
def start_game():
    word_count = WordList.query.count()
    if word_count == 0:
        return jsonify({'message': 'Error: No words configured in the database.'}), 500
        
    random_offset = random.randint(0, word_count - 1)
    target_word_record = WordList.query.offset(random_offset).first()
    target_word = target_word_record.word

    new_game = Game(
        user_id=session['user_id'],
        target_word=target_word
    )
    db.session.add(new_game)
    db.session.commit()
    
    user_id = session['user_id']
    today = date.today()
    games_played_today = Game.query.filter(
        Game.user_id == user_id,
        Game.date_played == today
    ).count()
    
    return jsonify({
        'message': 'Game started.',
        'game_id': new_game.id,
        'guesses_remaining': Config.MAX_GUESSES_PER_WORD,
        'words_left_today': Config.MAX_WORDS_PER_DAY - games_played_today,
        'status': new_game.status
    }), 200


# Submit Guess Route
@bp.route('/api/game/guess', methods=['POST'])
@login_required
def submit_guess():
    data = request.get_json()
    game_id = data.get('game_id')
    guessed_word = data.get('guess', '').upper()

    # 1. Retrieve the current game
    game = Game.query.filter_by(id=game_id, user_id=session['user_id']).first()

    if not game:
        return jsonify({'message': 'Game not found or access denied.'}), 404
        
    if game.status != 'in_progress':
        return jsonify({'message': f'Game already concluded with a {game.status}.'}), 400
        
    # 2. Validate guess word format
    if len(guessed_word) != Config.WORD_LENGTH or not guessed_word.isalpha():
        return jsonify({'message': f'Guess must be a {Config.WORD_LENGTH}-letter word (uppercase only).'}), 400
        
    # 3. Check guess limit
    current_guess_count = game.guesses.count()
    if current_guess_count >= Config.MAX_GUESSES_PER_WORD:
        game.status = 'loss'
        db.session.commit()
        return jsonify({'message': 'Max guesses reached. Game Over.'}), 400

    # 4. Calculate feedback
    target_word = game.target_word
    feedback_json = calculate_guess_feedback(target_word, guessed_word)
    
    # 5. Create new Guess entry
    new_guess = Guess(
        game_id=game.id,
        guess_word=guessed_word,
        guess_number=current_guess_count + 1,
        feedback_json=feedback_json
    )
    db.session.add(new_guess)

    # 6. Check for WIN/LOSS condition
    is_win = (guessed_word == target_word)
    is_last_guess = (current_guess_count + 1) == Config.MAX_GUESSES_PER_WORD
    
    target_word_reveal = None
    if is_win:
        game.status = 'win'
        message = 'Congratulations! You guessed the word!'
        target_word_reveal = target_word
    elif is_last_guess:
        game.status = 'loss'
        message = f"Better luck next time. The word was **{target_word}**."
        target_word_reveal = target_word
    else:
        message = 'Keep guessing.'

    db.session.commit()
    
    # 7. Return game state and feedback
    return jsonify({
        'message': message,
        'guess_number': new_guess.guess_number,
        'feedback': json.loads(feedback_json),
        'game_status': game.status,
        'guesses_remaining': Config.MAX_GUESSES_PER_WORD - (current_guess_count + 1),
        'target_word': target_word_reveal
    }), 200
    
# Daily Report Route
@bp.route('/api/admin/report/daily', methods=['GET'])
@admin_required
def daily_report():
    """
    Provides a report for a specific day: 
    (number of users who played, number of correct guesses/wins).
    Expects 'date' query parameter in YYYY-MM-DD format.
    """
    report_date_str = request.args.get('date')
    
    if not report_date_str:
        return jsonify({'message': 'Date parameter (YYYY-MM-DD) is required.'}), 400
        
    try:
        report_date = date.fromisoformat(report_date_str)
    except ValueError:
        return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    # Number of unique users who played
    unique_users_count = db.session.query(db.func.count(db.func.distinct(Game.user_id))).filter(
        Game.date_played == report_date
    ).scalar()

    # Number of correct guesses (wins)
    correct_guesses_count = Game.query.filter(
        Game.date_played == report_date,
        Game.status == 'win'
    ).count()

    return jsonify({
        'date': report_date_str,
        'unique_players': unique_users_count or 0,
        'total_wins': correct_guesses_count or 0
    }), 200


# User Report Route
@bp.route('/api/admin/report/user/<string:username>', methods=['GET'])
@admin_required
def user_report(username):
    """
    Provides a report for a specific user: 
    (date, number of words tried, and number of correct guesses).
    """
    search_username_lower = username.lower()
    user = User.query.filter(
        db.func.lower(User.username) == search_username_lower
    ).first()

    if not user:
        return jsonify({'message': f'User "{username}" not found.'}), 404

    # Group games by the date played
    daily_stats = db.session.query(
        Game.date_played,
        db.func.count(Game.id).label('words_tried'),
        db.func.sum(db.case((Game.status == 'win', 1), else_=0)).label('correct_guesses')
    ).filter(
        Game.user_id == user.id
    ).group_by(Game.date_played).order_by(Game.date_played.desc()).all()

    report_data = []
    for stat in daily_stats:
        report_data.append({
            'date': stat.date_played.isoformat(),
            'words_tried': stat.words_tried,
            'correct_guesses': stat.correct_guesses
        })

    return jsonify({
        'username': username,
        'user_id': user.id,
        'report': report_data
    }), 200
    

@bp.route('/api/admin/report/all_users', methods=['GET'])
@admin_required
def all_users_report():
    """
    Provides statistics for ALL player users (total words tried, total wins).
    """
    all_stats = db.session.query(
        User.username,
        db.func.count(Game.id).label('total_words_tried'),
        db.func.sum(db.case((Game.status == 'win', 1), else_=0)).label('total_wins')
    ).join(Game, User.id == Game.user_id, isouter=True 
    ).filter(
        User.role == 'player'
    ).group_by(User.id, User.username).all()

    report_data = []
    for stat in all_stats:
        report_data.append({
            'username': stat.username,
            'total_words_tried': stat.total_words_tried or 0,
            'total_wins': stat.total_wins or 0
        })

    return jsonify({'report': report_data}), 200