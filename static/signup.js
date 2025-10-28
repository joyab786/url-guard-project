// signup.js
document.getElementById('signup-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const fullname = document.getElementById('fullname').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    if (password !== confirmPassword) {
        alert("Passwords do not match!");
        return;
    }

    try {
        // ===== START: ERROR FIX =====
        // Use a relative path so it works on any server
        const response = await fetch('/signup/', {
        // ===== END: ERROR FIX =====
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ fullname, email, password }),
        });
        
        const data = await response.json();

        if (!response.ok) {
            alert(data.detail || 'An error occurred.');
        } else {
            alert(data.message);
            // Use a relative path for the redirect
            window.location.href = '/login.html'; // Redirect to login page on success
        }
    } catch (error) {
        alert('Could not connect to the server.');
    }
});