document.addEventListener('DOMContentLoaded', () => {
    // DOM Element Selection
    const dailyReportForm = document.getElementById('daily-report-form');
    const reportDateInput = document.getElementById('report-date');
    const dailyDateDisplay = document.getElementById('daily-date-display');
    const dailyPlayersCount = document.getElementById('daily-players-count');
    const dailyWinsCount = document.getElementById('daily-wins-count');

    const userReportForm = document.getElementById('user-report-form');
    const userSearchInput = document.getElementById('user-search');
    const userReportUsername = document.getElementById('user-report-username');
    const userHistoryBody = document.getElementById('user-history-body');

    const allUsersReportButton = document.getElementById('all-users-report-button');
    const allUsersBody = document.getElementById('all-users-body');

    const messageArea = document.getElementById('message-area');

    // Helper Function to Display Messages
    function displayMessage(message, type = 'error') {
        messageArea.textContent = message;
        messageArea.className = 'alert-box'; // Reset class
        if (message) {
            messageArea.classList.add(type === 'success' ? 'alert-success' : 'alert-error');
        } else {
            messageArea.textContent = '';
        }
    }

    // Helper Function for API Calls (Admin specific, includes error handling) 
    async function apiFetchAdmin(url) {
        try {
            const response = await fetch(url);
            const data = await response.json();
            
            if (!response.ok) {
                displayMessage(`Error: ${data.message}`, 'error');
                return null;
            }
            displayMessage('', 'success'); 
            return data;
        } catch (error) {
            console.error('API Error:', error);
            displayMessage('A network error occurred or the API is unreachable.', 'error');
            return null;
        }
    }

    // Daily Report Logic 

    dailyReportForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const selectedDate = reportDateInput.value;
        if (!selectedDate) {
            displayMessage('Please select a date.', 'error');
            return;
        }
        
        const url = `/api/admin/report/daily?date=${selectedDate}`;
        const data = await apiFetchAdmin(url);

        if (data) {
            dailyDateDisplay.textContent = data.date;
            dailyPlayersCount.textContent = data.unique_players;
            dailyWinsCount.textContent = data.total_wins;
            displayMessage('Daily report generated successfully.', 'success');
        } else {
            dailyDateDisplay.textContent = '--';
            dailyPlayersCount.textContent = 0;
            dailyWinsCount.textContent = 0;
        }
    });

    // Single User Report Logic 

    userReportForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = userSearchInput.value.trim(); 
        
        if (!username) {
            displayMessage('Please enter a username.', 'error');
            return;
        }
        
        const encodedUsername = encodeURIComponent(username);
        const url = `/api/admin/report/user/${encodedUsername}`;
        
        const data = await apiFetchAdmin(url);

        userHistoryBody.innerHTML = ''; 
        userReportUsername.textContent = username; 

        if (data) {
            if (data.report && data.report.length > 0) {
                data.report.forEach(day => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td style="padding: 8px; border: 1px solid var(--color-dark-wood);">${day.date}</td>
                        <td style="padding: 8px; border: 1px solid var(--color-dark-wood); text-align: center;">${day.words_tried}</td>
                        <td style="padding: 8px; border: 1px solid var(--color-dark-wood); text-align: center;">${day.correct_guesses}</td>
                    `;
                    userHistoryBody.appendChild(row);
                });
                displayMessage(`History found for user: ${username}`, 'success');
            } else {
                // User found, but no games played
                userReportUsername.textContent = `${username} (No games played)`;
                const row = document.createElement('tr');
                row.id = 'user-report-placeholder';
                row.innerHTML = `<td colspan="3" style="text-align: center; padding: 10px;">User found, but no game history available.</td>`;
                userHistoryBody.appendChild(row);
                displayMessage(`User ${username} found. No game history yet.`, 'success');
            }
        } else {
            // User not found
            userReportUsername.textContent = `${username} (Not Found)`;
            const row = document.createElement('tr');
            row.id = 'user-report-placeholder';
            row.innerHTML = `<td colspan="3" style="text-align: center; padding: 10px;">User not found.</td>`;
            userHistoryBody.appendChild(row);
        }
    });
    
    // All Users Report Logic 

    allUsersReportButton.addEventListener('click', async () => {
        const url = `/api/admin/report/all_users`;
        const data = await apiFetchAdmin(url);

        allUsersBody.innerHTML = ''; 
        
        if (data && data.report) {
            if (data.report.length > 0) {
                data.report.forEach(player => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td style="padding: 8px; border: 1px solid var(--color-antique-gold);">${player.username}</td>
                        <td style="padding: 8px; border: 1px solid var(--color-antique-gold); text-align: center;">${player.total_words_tried}</td>
                        <td style="padding: 8px; border: 1px solid var(--color-antique-gold); text-align: center;">${player.total_wins}</td>
                    `;
                    allUsersBody.appendChild(row);
                });
                displayMessage('Global rankings loaded successfully.', 'success');
            } else {
                const row = document.createElement('tr');
                row.id = 'all-users-placeholder';
                row.innerHTML = `<td colspan="3" style="text-align: center; padding: 10px;">No player data available.</td>`;
                allUsersBody.appendChild(row);
                displayMessage('No player data found.', 'error');
            }
        } else {
            // Error handled by apiFetchAdmin
            const row = document.createElement('tr');
            row.id = 'all-users-placeholder';
            row.innerHTML = `<td colspan="3" style="text-align: center; padding: 10px;">Failed to load player rankings.</td>`;
            allUsersBody.appendChild(row);
        }
    });
});