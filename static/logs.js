document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('form').addEventListener('submit', function (event) {
        event.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        authenticate(username, password);
    });

    async function authenticate(username, password) {
        const userIds = await fetchUserIds(username, password);
        if (userIds) {
            populateUserDropdown(userIds);
        }
    }

    async function fetchUserIds(username, password) {
        const response = await fetch('/user_ids', {
            headers: {
                'Accept': 'application/json',
                'dev-username': username,
                'dev-password': password,
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                alert('Unauthorized');
            } else {
                alert(`An error occurred: ${response.status} ${response.statusText}`);
            }
            return null;
        }

        return await response.json();
    }

    function populateUserDropdown(userIds) {
        const userSelect = document.getElementById('user-select');
        userSelect.innerHTML = ''; // Clear existing options

        userIds.forEach(userId => {
            const option = document.createElement('option');
            option.value = userId;
            option.textContent = userId;
            userSelect.appendChild(option);
        });

        document.getElementById('login-form').style.display = 'none';
        document.getElementById('user-dropdown').style.display = 'block';
    }

    document.getElementById('view-logs').addEventListener('click', function () {
        const userId = document.getElementById('user-select').value;
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        fetchLogs(userId, username, password);
    });

    function escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    async function fetchLogs(userId, username, password) {
        const response = await fetch('/logs', {
            headers: {
                'Accept': 'application/json',
                'dev-username': username,
                'dev-password': password,
                'user-id': userId,
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                alert('Unauthorized');
            } else {
                alert(`An error occurred: ${response.status} ${response.statusText}`);
            }
            return false;
        }

        const logs = await response.json();
        const logEntries = document.getElementById('log-entries');
        logEntries.innerHTML = ''; // Clear existing entries

        // Sort logs by time
        logs.sort((a, b) => new Date(b.time) - new Date(a.time));

        // Group logs by day
        const groupedLogs = logs.reduce((acc, log) => {
            const date = new Date(log.time).toLocaleDateString("de-DE");
            if (!acc[date]) {
                acc[date] = [];
            }
            acc[date].push(log);
            return acc;
        }, {});

        // Create table rows for each day
        for (const [date, logs] of Object.entries(groupedLogs)) {
            const dateRow = document.createElement('tr');
            dateRow.innerHTML = `<td colspan="3" style="background-color: #e0e0e0; font-weight: bold;">${date}</td>`;
            logEntries.appendChild(dateRow);

            logs.forEach(log => {
                const logDate = new Date(log.time);
                const row = document.createElement('tr');
                row.className = log.level.toLowerCase();
                row.innerHTML = `
                    <td class="log-date"><span class="date">${logDate.toLocaleDateString("de-DE")}</span> ${logDate.toLocaleTimeString("de-DE")}</td>
                    <td class="message">${escapeHtml(log.message)}</td>
                    <td>${log.level}</td>
                `;
                logEntries.appendChild(row);
            });
        }

        document.getElementById('log-viewer').style.display = 'block';

        // Add click event listener to expand messages
        document.querySelectorAll('.message').forEach(message => {
            message.addEventListener('click', function () {
                const logDate = this.previousElementSibling;
                const dateSpan = logDate.querySelector('.date');
                if (this.style.webkitLineClamp === '3') {
                    this.style.webkitLineClamp = 'unset';
                    dateSpan.style.display = 'inline';
                } else {
                    this.style.webkitLineClamp = '3';
                    dateSpan.style.display = 'none';
                }
            });
        });

        return true;
    }
});