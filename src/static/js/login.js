document.addEventListener('DOMContentLoaded', function() {
    // Tab switching functionality
    const loginTab = document.getElementById('login-tab');
    const registerTab = document.getElementById('register-tab');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    
    // Show login form by default
    loginTab.classList.add('active');
    registerForm.style.display = 'none';
    
    // Switch to login tab
    loginTab.addEventListener('click', function() {
        loginTab.classList.add('active');
        registerTab.classList.remove('active');
        loginForm.style.display = 'block';
        registerForm.style.display = 'none';
    });
    
    // Switch to register tab
    registerTab.addEventListener('click', function() {
        registerTab.classList.add('active');
        loginTab.classList.remove('active');
        registerForm.style.display = 'block';
        loginForm.style.display = 'none';
    });
    
    // Remove role and category selection functionality as we're simplifying registration
    
    // Form validation
    function validateLoginForm() {
        const email = document.getElementById('login-email').value.trim();
        const password = document.getElementById('login-password').value.trim();
        
        if (!email) {
            showValidationError('login-email', 'Email is required');
            return false;
        }
        
        if (!validateEmail(email)) {
            showValidationError('login-email', 'Please enter a valid email address');
            return false;
        }
        
        if (!password) {
            showValidationError('login-password', 'Password is required');
            return false;
        }
        
        return true;
    }
    
    function validateRegisterForm() {
        const email = document.getElementById('register-email').value.trim();
        const password = document.getElementById('register-password').value.trim();
        const confirmPassword = document.getElementById('register-confirm-password').value.trim();
        
        // Reset previous errors
        clearValidationErrors();
        
        if (!email) {
            showValidationError('register-email', 'Email is required');
            return false;
        }
        
        if (!validateEmail(email)) {
            showValidationError('register-email', 'Please enter a valid email address');
            return false;
        }
        
        if (!password) {
            showValidationError('register-password', 'Password is required');
            return false;
        }
        
        if (password.length < 6) {
            showValidationError('register-password', 'Password must be at least 6 characters');
            return false;
        }
        
        if (password !== confirmPassword) {
            showValidationError('register-confirm-password', 'Passwords do not match');
            return false;
        }
        
        return true;
    }
    
    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
    
    function showValidationError(inputId, message) {
        const input = document.getElementById(inputId);
        input.classList.add('is-invalid');
        
        // Create error message element
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        
        // Add error message after input
        input.parentNode.appendChild(errorDiv);
    }
    
    function clearValidationErrors() {
        // Remove all error messages
        document.querySelectorAll('.invalid-feedback').forEach(el => el.remove());
        
        // Remove invalid class from inputs
        document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
    }
    
    // Add form validation to login form
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            clearValidationErrors();
            if (!validateLoginForm()) {
                e.preventDefault();
            }
        });
    }
    
    // Add form validation to register form
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            if (!validateRegisterForm()) {
                e.preventDefault();
            }
        });
    }
    
    // Clear validation errors when inputs change
    document.querySelectorAll('input').forEach(input => {
        input.addEventListener('input', function() {
            this.classList.remove('is-invalid');
            const feedback = this.parentNode.querySelector('.invalid-feedback');
            if (feedback) {
                feedback.remove();
            }
        });
    });
});
