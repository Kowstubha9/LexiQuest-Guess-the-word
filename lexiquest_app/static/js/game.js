document.addEventListener('DOMContentLoaded', () => {
    // DOM Element Selection and Global Variables 
    const startGameButton = document.getElementById('start-game-button');
    const playAgainButton = document.getElementById('play-again-button');
    const guessForm = document.getElementById('guess-form');
    const guessInput = document.getElementById('guess-input');
    const submitGuessButton = document.getElementById('submit-guess-button');
    
    const gameStartArea = document.getElementById('game-start-area');
    const activeGameArea = document.getElementById('active-game-area');
    const gameEndControls = document.getElementById('game-end-controls');
    const wordGridDisplay = document.getElementById('word-grid-display');
    const gameStatusMessage = document.getElementById('game-status-message');
    const guessesCountSpan = document.getElementById('guesses-count');
    const dailyWordsLeftSpan = document.getElementById('daily-words-left'); 
    
    // Game State variables
    let currentGameId = null;
    let currentGuessNumber = 0;
    const WORD_LENGTH = 5; 
    const MAX_GUESSES = 5;

    // Helper Function to Display Game Messages 
    function displayGameMessage(message, color = 'var(--color-dark-wood)') {
        gameStatusMessage.innerHTML = message;
        gameStatusMessage.style.color = color;
    }

    // Helper Function for API Calls 
    async function apiFetch(url, method = 'GET', body = null) {
        try {
            const options = {
                method: method,
                headers: { 'Content-Type': 'application/json' },
            };
            if (body) {
                options.body = JSON.stringify(body);
            }
            const response = await fetch(url, options);
            const data = await response.json();
            
            if (!response.ok) {
                displayGameMessage(`Error: ${data.message}`, 'red');
                if (response.status === 401 || response.status === 403) {
                    updateDailyWordCount(0); 
                    gameStartArea.style.display = 'block';
                    activeGameArea.style.display = 'none';
                }
                return null;
            }
            return data;
        } catch (error) {
            console.error('API Error:', error);
            displayGameMessage('A network error occurred. Please check your connection.', 'red');
            return null;
        }
    }

    // Grid Management 
    function createEmptyGrid() {
        wordGridDisplay.innerHTML = '';
        for (let i = 0; i < MAX_GUESSES; i++) {
            const row = document.createElement('div');
            row.classList.add('grid-row');
            row.id = `row-${i + 1}`;
            for (let j = 0; j < WORD_LENGTH; j++) {
                const tile = document.createElement('div');
                tile.classList.add('letter-tile');
                tile.id = `tile-${i + 1}-${j + 1}`;
                row.appendChild(tile);
            }
            wordGridDisplay.appendChild(row);
        }
    }

    function renderGuess(guessNumber, feedback) {
        const row = document.getElementById(`row-${guessNumber}`);
        if (!row || !feedback || feedback.length !== WORD_LENGTH) return;

        feedback.forEach((item, index) => {
            const tile = row.children[index];
            tile.textContent = item.l;
            tile.classList.add(`tile-${item.c}`);
        });
    }
    
    // Update Daily Word Count
    function updateDailyWordCount(count) {
        if (dailyWordsLeftSpan) {
            dailyWordsLeftSpan.textContent = count;
            
            if (count <= 0) {
                startGameButton.disabled = true;
                playAgainButton.disabled = true;
                displayGameMessage(`You have played all words for today!`, 'red');
            } else {
                startGameButton.disabled = false;
                playAgainButton.disabled = false;
            }
        }
    }

    // Game State Control 

    function initializeGame(data) {
        currentGameId = data.game_id;
        currentGuessNumber = 0;
        
        gameStartArea.style.display = 'none';
        gameEndControls.style.display = 'none';
        activeGameArea.style.display = 'block';
        
        createEmptyGrid();

        guessInput.value = '';
        guessInput.disabled = false;
        submitGuessButton.disabled = false;

        updateDailyWordCount(data.words_left_today); 
        
        guessesCountSpan.textContent = MAX_GUESSES;
        displayGameMessage('The quest has begun. Submit your first guess!');
    }
    
    function endGame(status, message, targetWord = null) {
        submitGuessButton.disabled = true;
        guessInput.disabled = true;

        if (status === 'win') {
            displayGameMessage(message, 'var(--color-green)');
        } else if (status === 'loss') {
            displayGameMessage(message, 'red');
        }

        gameEndControls.style.display = 'block';
        currentGameId = null; 
    }

    // Event Handlers 

    startGameButton.addEventListener('click', async () => {
        const data = await apiFetch('/api/game/start', 'POST');
        if (data) {
            initializeGame(data); 
        }
    });

    playAgainButton.addEventListener('click', async () => {
        const data = await apiFetch('/api/game/start', 'POST');
        if (data) {
            initializeGame(data); 
        } else {
            gameEndControls.style.display = 'none';
            gameStartArea.style.display = 'block';
        }
    });

    guessForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!currentGameId) {
            displayGameMessage('Please start a new game first.', 'red');
            return;
        }

        const guess = guessInput.value.trim().toUpperCase();

        if (guess.length !== WORD_LENGTH || !/^[A-Z]+$/.test(guess)) {
            displayGameMessage(`The word must be ${WORD_LENGTH} letters long and contain only letters.`, 'red');
            return;
        }
        
        submitGuessButton.disabled = true;

        const data = await apiFetch('/api/game/guess', 'POST', {
            game_id: currentGameId,
            guess: guess
        });
        
        if (data) {
            if (data.game_status === 'in_progress') {
                submitGuessButton.disabled = false;
            }
            
            currentGuessNumber = data.guess_number;
            renderGuess(data.guess_number, data.feedback);
            
            guessInput.value = '';
            guessInput.focus();

            guessesCountSpan.textContent = data.guesses_remaining;

            if (data.game_status !== 'in_progress') {
                endGame(data.game_status, data.message, data.target_word);
            } else {
                displayGameMessage(data.message);
            }
        }
    });
    
    // Initial Setup Check
    if (guessInput) {
        guessInput.addEventListener('input', () => {
            guessInput.value = guessInput.value.toUpperCase().replace(/[^A-Z]/g, '');
            submitGuessButton.disabled = guessInput.value.length !== WORD_LENGTH;
        });
    }
});