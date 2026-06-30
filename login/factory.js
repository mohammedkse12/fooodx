// انتظام عمل الكود بعد تحميل الصفحة بالكامل
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

    // 3. التنبيه عند إرسال النموذج ومنع إعادة التحميل السريعة
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function (event) {
            //  : يمنع المتصفح من إعادة تحميل الصفحة فوراً لنتمكن من رؤية الـ Alert
            event.preventDefault();

            alert('تم استلام بياناتك بنجاح! حسابك الآن "قيد المراجعة" وسيتم تفعيله قريباً بواسطة الإدارة.');

            // ملحوظة للمستقبل: عندما تربط الصفحة بسيرفر حقيقي، يمكنك تفعيل السطر التالي لإرسال البيانات فعلياً:
            // form.submit();
        });
    }
});