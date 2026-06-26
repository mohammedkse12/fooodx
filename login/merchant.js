
// 1. ميزة إظهار وإخفاء كلمة المرور
const togglePassword = document.getElementById('togglePassword');
const passwordField = document.getElementById('passwordField');

togglePassword.addEventListener('click', function () {
    // التحقق من نوع الحقل الحالي وتغييره
    const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordField.setAttribute('type', type);

    // تغيير أيقونة العين
    this.textContent = type === 'password' ? 'اظهار' : 'اخفاء';
});

// 2. التحقق من الرقم الوطني قبل إرسال البيانات (Validation)
const form = document.querySelector('form');
const nationalIdInput = document.querySelector('input[name="national_id"]');

form.addEventListener('submit', function (event) {
    // التأكد من أن الرقم الوطني 11 رقم بالضبط
    const nationalIdValue = nationalIdInput.value.trim();

    if (nationalIdValue.length !== 11) {
        // منع إرسال النموذج للسيرفر
        event.preventDefault();
        // إظهار رسالة تنبيه للمستخدم
        alert('عذراً، يجب أن يتكون الرقم الوطني من 11 رقماً بالضبط.');
        nationalIdInput.focus(); // توجيه المؤشر لحقل الرقم الوطني
        nationalIdInput.style.borderColor = '#e74c3c'; // تغيير لون الإطار للأحمر
    }
});

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