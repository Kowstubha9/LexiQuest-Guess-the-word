document.addEventListener('DOMContentLoaded', () => {
    // DOM Element Selection 
    const loginSection = document.getElementById('login-section');
    const registerSection = document.getElementById('register-section');
    const showRegisterLink = document.getElementById('show-register');
    const showLoginLink = document.getElementById('show-login');
    
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const logoutButton = document.getElementById('logout-button');

    const messageArea = document.getElementById('message-area');

    // Helper Function to Display Messages 
    function displayMessage(message, type = 'error') {
        messageArea.textContent = message;
        messageArea.className = 'alert-box'; 
        if (message) {
            messageArea.classList.add(type === 'success' ? 'alert-success' : 'alert-error');
        } else {
            messageArea.textContent = '';
        }
    }

    // Form Switching Logic (for index.html) 
    if (showRegisterLink && showLoginLink) {
        showRegisterLink.addEventListener('click', (e) => {
            e.preventDefault();
            loginSection.style.display = 'none';
            registerSection.style.display = 'block';
            displayMessage(''); 
        });

        showLoginLink.addEventListener('click', (e) => {
            e.preventDefault();
            registerSection.style.display = 'none';
            loginSection.style.display = 'block';
            displayMessage(''); 
        });
    }

    // Registration Handler 
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            displayMessage(''); 

            const username = document.getElementById('register-username').value;
            const password = document.getElementById('register-password').value;

            try {
                const response = await fetch('/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, password })
                });

                const data = await response.json();

                if (response.ok) {
                    displayMessage(data.message, 'success');
                    setTimeout(() => {
                        registerSection.style.display = 'none';
                        loginSection.style.display = 'block';
                        displayMessage(''); 
                    }, 500); 
                } else {
                    displayMessage(data.message);
                }
            } catch (error) {
                console.error('Registration failed:', error);
                displayMessage('An unexpected error occurred during registration.');
            }
        });
    }


    // Login Handler 
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            displayMessage(''); 

            const username = document.getElementById('login-username').value;
            const password = document.getElementById('login-password').value;

            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, password })
                });

                const data = await response.json();

                if (response.ok) {
                    displayMessage(data.message, 'success');
                    window.location.href = data.redirect_url;
                } else {
                    displayMessage(data.message);
                }
            } catch (error) {
                console.error('Login failed:', error);
                displayMessage('An unexpected error occurred during login.');
            }
        });
    }

    // Logout Handler 
    if (logoutButton) {
        logoutButton.addEventListener('click', async () => {
            try {
                const response = await fetch('/logout', {
                    method: 'POST',
                });

                const data = await response.json();

                if (response.ok) {
                    alert(data.message); 
                    window.location.href = '/';
                } else {
                    displayMessage(data.message);
                }
            } catch (error) {
                console.error('Logout failed:', error);
                window.location.href = '/'; 
            }
        });
    }
});