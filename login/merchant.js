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

    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', async function(event) {
            event.preventDefault();

            const submitButton = form.querySelector('button[type="submit"]');
            const originalText = submitButton ? submitButton.textContent : 'إنشاء الحساب';
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.textContent = 'جاري الإرسال...';
            }

            try {
                const formData = new FormData(form);
                const response = await fetch('http://localhost:5000/api/auth/merchant/register', {
                    method: 'POST',
                    body: formData,
                });
                const data = await response.json().catch(() => ({}));

                if (!response.ok) {
                    throw new Error(data.error || 'فشل إنشاء الحساب');
                }

                alert(data.message || 'تم إنشاء الحساب بنجاح');
                form.reset();
            } catch (error) {
                alert(error.message || 'حدث خطأ غير متوقع');
            } finally {
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.textContent = originalText;
                }
            }
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