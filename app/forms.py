from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp

class factorySignup(FlaskForm):
    # --- Existing Fields ---
    username = StringField('اسم المستخدم', validators=[DataRequired(), Length(min=10, max=30)])
    factory_name = StringField('اسم المصنع', validators=[DataRequired(), Length(min=2, max=50)])
    
    # Note: Added a sample regex pattern since empty regexp() throws an error
    password = PasswordField('كلمة المرور', validators=[
        DataRequired(), 
        Length(min=8, max=25),
        Regexp(r'^[A-Za-z\d@$!%*?&]+$', message="كلمة المرور تحتوي على رموز غير مسموحة")
    ])
    
    email = StringField('البريد الالكتروني', validators=[DataRequired(), Email()])
    
    # Changed to StringField (See Senior Review Notes below)
    phone = StringField('رقم الهاتف', validators=[
        DataRequired(), 
        Length(min=9, max=12),
        Regexp(r'^\d+$', message="يجب إدخال أرقام فقط")
    ])

    # --- New Fields (Based on UI) ---
    
    location = StringField('الموقع بالتفصيل', validators=[DataRequired()])
    
    shipping_available = RadioField('هل تتوفر لديكم وسيلة شحن / توصيل للطلبات؟', 
                              choices=[('yes', 'نعم'), ('no', 'لا')], 
                              validators=[DataRequired()])
    
    commercial_register = StringField('رقم السجل التجاري', validators=[
        DataRequired(),
        Regexp(r'^\d+$', message="يجب إدخال أرقام فقط")
    ])
    
    submit = SubmitField('إرسال طلب التسجيل')

class merchantSignupForm(FlaskForm):
    # --- Basic Data (البيانات الأساسية) ---
    username = StringField('اسم المستخدم', validators=[
        DataRequired(), 
        Length(min=4, max=30)
    ])
    
    password = PasswordField('كلمة المرور', validators=[
        DataRequired(), 
        Length(min=8, max=32)
    ])
    
    email = StringField('البريد الإلكتروني', validators=[
        DataRequired(), 
        Email(message="يرجى إدخال بريد إلكتروني صحيح")
    ])
    
    # Keeping this as a StringField, just like we did for the Factory form!
    phone = StringField('رقم الهاتف', validators=[
        DataRequired(), 
        Length(min=9, max=12),
        Regexp(r'^\d+$', message="يجب إدخال أرقام فقط")
    ])
    
    other_location = StringField('الموقع بالتفصيل', validators=[
        DataRequired()
    ])
    
    # --- Documentation and Legal Data (التوثيق والبيانات القانونية) ---
    
    # The UI specifies exactly 11 digits, so we lock min and max to 11.
    national_id = StringField('الرقم الوطني', validators=[
        Length(min=11, message="الرقم الوطني يجب أن يتكون من 11 رقم على الأقل")
    ])
    
    submit = SubmitField('إنشاء الحساب')
class LoginForm(FlaskForm):
    user_id = StringField('اسم المستخدم أو المعرف (ID)', validators=[
        DataRequired(message="يرجى إدخال اسم المستخدم أو المعرف")
    ])
    password = PasswordField('كلمة المرور', validators=[
        DataRequired(message="يرجى إدخال كلمة المرور")
    ])
    submit = SubmitField('تسجيل الدخول')
