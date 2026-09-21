document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const errorMessage = document.getElementById('errorMessage');

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        errorMessage.style.display = 'none';

        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value.trim();

        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                window.location.href = '/dashboard';
            } else {
                errorMessage.textContent = data.message || 'Invalid username or password';
                errorMessage.style.display = 'block';
            }
        } catch (err) {
            errorMessage.textContent = 'Server error. Make sure Flask server is running on port 5001.';
            errorMessage.style.display = 'block';
        }
    });
});
