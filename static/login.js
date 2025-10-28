// login.js
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    const loginButton = document.querySelector('.login-button');
    loginButton.textContent = 'Logging in...';
    loginButton.disabled = true;

    try {
        // Use a relative path so it works on any server
        const response = await fetch('/token', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
        });

        const data = await response.json();

        if (!response.ok) {
            // If login fails, FastAPI sends details in the 'detail' key
            alert(data.detail || 'An unknown error occurred.');
        } else {
            alert('Login successful!');
            // Redirect to the main homepage
            window.location.href = '/';
        }
    } catch (error) {
        console.error('Login error:', error);
        alert('Could not connect to the server. Please ensure it is running.');
    } finally {
        loginButton.textContent = 'Login';
        loginButton.disabled = false;
    }
});