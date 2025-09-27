# 🗺️ LexiQuest: The Word Quest Adventure



**LexiQuest** is a full-stack, Wordle-style guessing game built with a secure, multi-user architecture. Players strive to decipher a 5-letter hidden word in five attempts or less. The project is designed with a strong separation between client-side and server-side responsibilities, featuring robust user management and comprehensive administrator reporting tools.

## ✨ Key Features

* **Role-Based Access:** Separate environments for **Player** (game access) and **Admin** (reports access).
* **Secure Authentication:** User registration enforced with minimum length, alpha, numeric, and specific special character requirements (`$, %, *, @`).
* **Themed UI:** Uses a warm **Parchment and Antique Gold** color palette to evoke a "Word Quest" theme.
* **Core Game Mechanics:**
    * **Feedback:** Implements Green (Correct/Position), Orange (Correct/Wrong Position), and Grey (Not in Word) tile feedback.
    * **Constraints:** Enforces a maximum of **3 words** to guess per user per day, and **5 guesses** per word.
* **Admin Reporting:**
    * **Daily Summary:** View the total unique players and total wins for a selected date.
    * **User History:** Case-insensitive search to fetch detailed history for any player (date, games tried, wins).
    * **Global Rankings (Enhancement):** Overview of total games played and total wins for all players.

***

## 🚀 Technologies Used

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend** | **Python (Flask)** | REST API, session management, and core game logic. |
| **Database** | **MySQL** | Persistent storage for users, words, and game history. |
| **ORM** | **SQLAlchemy** | Object Relational Mapping for Python-to-MySQL data handling. |
| **Frontend** | **HTML5, CSS3, JavaScript** | Themed user interface and dynamic game rendering. |
| **Security** | **Werkzeug** | Secure password hashing. |

***

## ⚙️ Setup and Installation

Follow these steps to set up the LexiQuest server on your local machine.

### Prerequisites

* **Python 3.8+**
* **MySQL Server** (must be running)

### 1. Clone and Prepare the Environment
Clone the repository and activate the virtual environment

### 2. Install Dependencies
Install all required packages from requirements.txt:

### 3. Configure Database
Create Database: Log into your MySQL client and create the database specified in lexiquest_app/config.py (default: guessgame).
Update Connection: Ensure your database credentials are correct in lexiquest_app/config.py. 

### 4. Initialize Tables and Seed Data
Running the application for the first time will automatically create the necessary tables and seed the initial 20 words via db.create_all().

### 5. Run the Application
Set the mysql password and port number(if not default)
Execute the startup script from the project root using below command:
python run.py

