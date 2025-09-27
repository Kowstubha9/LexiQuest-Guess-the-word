import os
from urllib.parse import quote_plus

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_very_secret_and_complex_key_for_lexiquest'
    
    DB_USER = os.environ.get('MYSQL_USER') or 'root'
    DB_PASS = os.environ.get('MYSQL_PASSWORD') 
    DB_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    DB_PORT = os.environ.get('MYSQL_PORT') 
    DB_NAME = os.environ.get('MYSQL_DB') or 'guessgame'

    host_and_port = DB_HOST
    if DB_PORT:
        host_and_port = f"{DB_HOST}:{DB_PORT}"
    
    if DB_PASS:
        safe_db_pass = quote_plus(DB_PASS)
        
        SQLALCHEMY_DATABASE_URI = (
            f'mysql+pymysql://{DB_USER}:{safe_db_pass}@{host_and_port}/{DB_NAME}'
        )
    else:
        SQLALCHEMY_DATABASE_URI = None
        print("CRITICAL: MYSQL_PASSWORD environment variable is missing. Set it before running.")
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Game and User Constraints 
    MAX_GUESSES_PER_WORD = 5
    MAX_WORDS_PER_DAY = 3
    MIN_USERNAME_LENGTH = 5
    MIN_PASSWORD_LENGTH = 5
    
    # Word constraints
    WORD_LENGTH = 5