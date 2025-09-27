import re
import json
from lexiquest_app.config import Config
from collections import Counter 

# User Validation Logic 
def is_valid_username(username):
    """
    Check if the username meets the minimum length requirement.
    Username should have at least 5 letters (case-insensitive check for length).
    """
    return len(username) >= Config.MIN_USERNAME_LENGTH

def is_valid_password(password):
    """
    Password must be at least 5 characters long and contain:
    alpha, numeric, and one of special characters $, %, *, @.
    """
    if len(password) < Config.MIN_PASSWORD_LENGTH:
        return False

    if not re.search(r"[a-zA-Z]", password):
        return False

    if not re.search(r"\d", password):
        return False

    if not re.search(r"[$%*@]", password):
        return False
        
    return True

# Word Guessing Logic 

def calculate_guess_feedback(target_word, guessed_word):
    """
    Compares the guessed word to the target word and returns color feedback 
    (green, orange, grey) following Wordle-style logic.
    
    Target and Guessed words are expected to be 5-letter uppercase strings.
    Returns: A JSON string containing a list of dictionaries for each letter's feedback.
    e.g., '[{"l": "T", "c": "green"}, {"l": "O", "c": "green"}, ...]'
    """
    
    if len(target_word) != Config.WORD_LENGTH or len(guessed_word) != Config.WORD_LENGTH:
        return json.dumps([]) 

    feedback = []
    target_counts = Counter(target_word) 

    colors = ['grey'] * Config.WORD_LENGTH 

    for i in range(Config.WORD_LENGTH):
        guessed_letter = guessed_word[i]
        target_letter = target_word[i]
        
        if guessed_letter == target_letter:
            colors[i] = 'green'
            target_counts[guessed_letter] -= 1

    for i in range(Config.WORD_LENGTH):
        if colors[i] == 'green':
            continue
            
        guessed_letter = guessed_word[i]

        if target_counts[guessed_letter] > 0:
            colors[i] = 'orange'
            target_counts[guessed_letter] -= 1

    for i in range(Config.WORD_LENGTH):
        feedback.append({
            'l': guessed_word[i],
            'c': colors[i]
        })

    return json.dumps(feedback) 