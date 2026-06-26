document.addEventListener('DOMContentLoaded', function () {

    // 1. ميزة إظهار وإخفاء كلمة المرور
    const togglePassword = document.getElementById('togglePassword');
    const passwordField = document.getElementById('passwordField');

    if (togglePassword && passwordField) {
        togglePassword.addEventListener('click', function () {
            const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordField.setAttribute('type', type);
            this.textContent = type === 'password' ? 'اظهار' : 'اخفاء';
        });
    }

    // 2. معالجة إرسال الفورم (عرض Alert للتجربة ومنع الـ Refresh)
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function (event) {
            event.preventDefault(); // منع السيرفر مؤقتاً للمعاينة

            const userIdValue = document.getElementById('userId').value;
            alert('جاري التحقق من بيانات الحساب للمعرّف: ' + userIdValue);
        });
    }

});