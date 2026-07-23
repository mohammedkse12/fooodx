document.addEventListener('DOMContentLoaded', function() {

    // 1. ميزة إظهار وإخفاء كلمة المرور
    const togglePassword = document.getElementById('togglePassword');
    const passwordField = document.getElementById('passwordField');

    if (togglePassword && passwordField) {
        togglePassword.addEventListener('click', function() {
            const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordField.setAttribute('type', type);
            this.textContent = type === 'password' ? 'اظهار' : 'اخفاء';
        });
    }

    // 2. معالجة إرسال الفورم (عرض Alert للتجربة ومنع الـ Refresh)
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', async function(event) {
            event.preventDefault(); // منع السيرفر مؤقتاً للمعاينة

            const submitButton = form.querySelector('button[type="submit"]');
            const originalText = submitButton ? submitButton.textContent : 'تسجيل الدخول';
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.textContent = 'جاري تسجيل الدخول...';
            }

            try {
                const formData = new FormData(form);
                const response = await fetch('http://localhost:5000/api/auth/login', {
                    method: 'POST',
                    body: formData,
                });
                const data = await response.json().catch(() => ({}));

                if (!response.ok) {
                    throw new Error(data.error || 'فشل تسجيل الدخول');
                }

                alert(data.message || 'تم تسجيل الدخول بنجاح');
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

});