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

    // 2. ميزة الخيارات الأخرى (إظهار حقل المدينة عند اختيار "مدينة أخرى")
    const locationSelect = document.getElementById('locationSelect');
    const otherCityGroup = document.getElementById('otherCityGroup');
    const otherCityInput = document.getElementById('otherCityInput');

    if (locationSelect && otherCityGroup && otherCityInput) {
        locationSelect.addEventListener('change', function () {
            if (this.value === 'other') {
                otherCityGroup.style.display = 'block'; // إظهار الحقل
                otherCityInput.setAttribute('required', 'required'); // جعله إجبارياً
            } else {
                otherCityGroup.style.display = 'none'; // إخفاء الحقل
                otherCityInput.removeAttribute('required'); // إلغاء الإجبارية
                otherCityInput.value = ''; // تفريغ النص
            }
        });
    }

    // 3. التنبيه عند إرسال النموذج ومنع إعادة التحميل السريعة
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function (event) {
            // الكود السحري: يمنع المتصفح من إعادة تحميل الصفحة فوراً لنتمكن من رؤية الـ Alert
            event.preventDefault();

            alert('تم استلام بياناتك بنجاح! حسابك الآن "قيد المراجعة" وسيتم تفعيله قريباً بواسطة الإدارة.');

            // ملحوظة للمستقبل: عندما تربط الصفحة بسيرفر حقيقي، يمكنك تفعيل السطر التالي لإرسال البيانات فعلياً:
            // form.submit();
        });
    }
});