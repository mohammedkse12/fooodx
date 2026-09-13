document.addEventListener('DOMContentLoaded', function() {

    const togglePassword = document.getElementById('togglePassword');
    const passwordField = document.getElementById('passwordField');

    if (togglePassword && passwordField) {
        togglePassword.addEventListener('click', function() {
            const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordField.setAttribute('type', type);
            this.textContent = type === 'password' ? 'اظهار' : 'اخفاء';
        });
    }

    const locationSelect = document.getElementById('locationSelect');
    const otherCityGroup = document.getElementById('otherCityGroup');
    const otherCityInput = document.getElementById('otherCityInput');

    if (locationSelect && otherCityGroup && otherCityInput) {
        locationSelect.addEventListener('change', function() {
            if (this.value === 'other') {
                otherCityGroup.style.display = 'block';
                otherCityInput.setAttribute('required', 'required');
            } else {
                otherCityGroup.style.display = 'none';
                otherCityInput.removeAttribute('required');
                otherCityInput.value = '';
            }
        });
    }
});