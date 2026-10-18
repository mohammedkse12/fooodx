from flask import Flask, jsonify, render_template, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text
from .forms import factorySignup, merchantSignupForm, LoginForm
from flask_cors import CORS
import os
import time
import secrets
from dotenv import load_dotenv
from .config import db, Config
from .mailer import send_otp_email

# Load environment variables
load_dotenv()
# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Failed login attempt tracker: {ip: {"count": int, "locked_until": float}}
FAILED_LOGIN_ATTEMPTS = {}
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_SECONDS = 2 * 60 * 60  # 2 hours

def _get_client_ip():
    return request.headers.get('X-Forwarded-For', request.remote_addr)

def _is_locked_out(ip):
    entry = FAILED_LOGIN_ATTEMPTS.get(ip)
    if not entry:
        return False
    if entry["count"] >= MAX_FAILED_ATTEMPTS:
        if time.time() < entry["locked_until"]:
            return True
        else:
            del FAILED_LOGIN_ATTEMPTS[ip]
            return False
    return False

def _record_failed_attempt(ip):
    now = time.time()
    entry = FAILED_LOGIN_ATTEMPTS.get(ip)
    if entry and now < entry.get("locked_until", 0):
        entry["count"] += 1
        entry["locked_until"] = now + LOCKOUT_SECONDS
    elif entry:
        entry["count"] += 1
        if entry["count"] >= MAX_FAILED_ATTEMPTS:
            entry["locked_until"] = now + LOCKOUT_SECONDS
    else:
        FAILED_LOGIN_ATTEMPTS[ip] = {
            "count": 1,
            "locked_until": now + LOCKOUT_SECONDS
        }

def _reset_failed_attempts(ip):
    FAILED_LOGIN_ATTEMPTS.pop(ip, None)

# Enable CORS
CORS(app)

# Configuration
app.config['DEBUG'] = os.getenv('DEBUG', False)
app.config['ENV'] = os.getenv('FLASK_ENV', 'production')

# Apply one-time schema migrations (PostgreSQL is the root source)
with app.app_context():
    db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version VARCHAR PRIMARY KEY,
            applied_at TIMESTAMPTZ DEFAULT now()
        );
    """))
    applied = db.session.execute(
        text("SELECT version FROM schema_migrations WHERE version = 'v1'")
    ).fetchone()

    if not applied:
        db.session.execute(text(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS username VARCHAR(30) UNIQUE"
        ))
        db.session.execute(text(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(20)"
        ))
        db.session.execute(text(
            "ALTER TABLE manufacturers ADD COLUMN IF NOT EXISTS factory_name VARCHAR(100)"
        ))
        db.session.execute(
            text("INSERT INTO schema_migrations (version) VALUES ('v1')")
        )
        db.session.commit()

    applied_v2 = db.session.execute(
        text("SELECT version FROM schema_migrations WHERE version = 'v2'")
    ).fetchone()

    if not applied_v2:
        db.session.execute(text(
            "ALTER TABLE users ALTER COLUMN password TYPE VARCHAR(255)"
        ))
        db.session.execute(
            text("INSERT INTO schema_migrations (version) VALUES ('v2')")
        )
        db.session.commit()

# Routes
@app.route('/', methods=['GET'])
def home():
    """Home endpoint / Root redirect"""
    return redirect(url_for('login'))

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'FoodX API'
    }), 200


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        ip = _get_client_ip()

        if _is_locked_out(ip):
            flash('لقد تجاوزت عدد محاولات تسجيل الدخول المسموحة (5 محاولات). يمكنك المحاولة مرة أخرى بعد ساعتين.', 'danger')
            return render_template('login.html', form=form), 429

        user_id = request.form.get('user_id') or request.form.get('username')
        password = request.form.get('password')

        if not user_id or not password:
            flash('يرجى إدخال اسم المستخدم وكلمة المرور', 'danger')
            return render_template('login.html', form=form)

        sql = text("SELECT id, username, email, password, role FROM users WHERE username = :uid OR email = :uid;")
        result = db.session.execute(sql, {'uid': user_id}).fetchone()

        if result and check_password_hash(result[3], password):
            _reset_failed_attempts(ip)
            # Password correct -> require email OTP (2FA) before opening a session
            otp_code = str(secrets.randbelow(900000) + 100000)
            session['pending_login'] = {
                'user_id': result[0],
                'username': result[1],
                'email': result[2],
                'role': result[4],
                'otp_code': otp_code,
                'attempts': 0,
                'expires_at': time.time() + 600
            }
            sent = send_otp_email(result[2], otp_code)
            if not sent:
                flash('لم يتم تجهيز إعدادات إرسال البريد بعد. رمز التحقق للتجربة هو: ' + otp_code, 'info')
            else:
                flash('تم إرسال رمز التحقق (OTP) إلى بريدك الإلكتروني لتأكيد تسجيل الدخول.', 'info')
            return redirect(url_for('verify_otp'))
        else:
            _record_failed_attempt(ip)
            remaining = MAX_FAILED_ATTEMPTS - FAILED_LOGIN_ATTEMPTS.get(ip, {}).get("count", 0)
            if remaining > 0:
                flash(f'اسم المستخدم أو كلمة المرور غير صحيحة. متبقي {remaining} محاولات.', 'danger')
            else:
                flash('لقد تجاوزت عدد محاولات تسجيل الدخول المسموحة (5 محاولات). يمكنك المحاولة مرة أخرى بعد ساعتين.', 'danger')
    return render_template('login.html', form=form)


@app.route('/api/login', methods=(['POST','GET']))
def api_login():
    ip = _get_client_ip()

    if _is_locked_out(ip):
        return jsonify({
            'ok': False,
            'message': 'لقد تجاوزت عدد محاولات تسجيل الدخول المسموحة (5 محاولات). يمكنك المحاولة مرة أخرى بعد ساعتين.'
        }), 429

    data = None
    try:
        data = request.get_json(force=True)
    except Exception:
        pass

    if not data:
        data = dict(request.form)

    user_id = data.get('user_id') if isinstance(data, dict) else None
    password = data.get('password') if isinstance(data, dict) else None

    sql = text("SELECT id, username, email, password, role FROM users WHERE username = :uid OR email = :uid;")
    result = db.session.execute(sql, {'uid': user_id}).fetchone()

    if result and check_password_hash(result[3], password):
        _reset_failed_attempts(ip)
        return jsonify({'ok': True, 'message': 'login successful', 'user': {'id': user_id}}), 200
    else:
        _record_failed_attempt(ip)
        remaining = MAX_FAILED_ATTEMPTS - FAILED_LOGIN_ATTEMPTS.get(ip, {}).get("count", 0)
        msg = 'invalid credentials'
        if remaining <= 0:
            msg = 'لقد تجاوزت عدد محاولات تسجيل الدخول المسموحة (5 محاولات). يمكنك المحاولة مرة أخرى بعد ساعتين.'
        else:
            msg = f'invalid credentials. {remaining} attempts remaining.'
        return jsonify({'ok': False, 'message': msg}), 401


@app.route('/factory/signup', methods=['GET', 'POST'])
def factory_signup():
    form = factorySignup()
    if form.validate_on_submit():
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            factory_name = request.form.get('factory_name') or request.form.get('factoryName')
            email = request.form.get('email')
            phone = request.form.get('phone')
            location = request.form.get('location') or request.form.get('detailed_location')
            shipping_available = request.form.get('shipping_available') or request.form.get('has_shipping')
            commercial_register = request.form.get('commercial_register')

            # Check for existing username/email
            existing = db.session.execute(
                text("SELECT id FROM users WHERE username = :u OR email = :e"),
                {'u': username, 'e': email}
            ).fetchone()
            if existing:
                flash('يوجد حساب مسجل مسبقاً بنفس اسم المستخدم أو البريد الإلكتروني. إذا كان لك حساب بالفعل فبإمكانك تسجيل الدخول مباشرة.', 'danger')
                return render_template('factory_signup.html', form=form)

            hashed_password = generate_password_hash(password)

            # Generate OTP and store pending registration
            otp_code = str(secrets.randbelow(900000) + 100000)
            session['pending_signup'] = {
                'role': 'Manufacturer',
                'form_data': {
                    'username': username,
                    'email': email,
                    'phone': phone,
                    'factory_name': factory_name,
                    'location': location,
                    'shipping_available': shipping_available,
                    'commercial_register': commercial_register
                },
                'hashed_password': hashed_password,
                'email': email,
                'otp_code': otp_code,
                'attempts': 0,
                'expires_at': time.time() + 600  # 10 minutes
            }

            sent = send_otp_email(email, otp_code)
            if not sent:
                flash('لم يتم تجهيز إعدادات إرسال البريد بعد. رمز التحقق للتجربة هو: ' + otp_code, 'info')
            else:
                flash('تم إرسال رمز التحقق (OTP) إلى بريدك الإلكتروني. يرجى التحقق من صندوق الوارد.', 'info')
            return redirect(url_for('verify_otp'))

        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء التسجيل: {str(e)}', 'danger')
    return render_template('factory_signup.html', form=form)


@app.route('/merchant/signup', methods=['GET', 'POST'])
def merchant_signup():
    form = merchantSignupForm()
    if form.validate_on_submit():
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            email = request.form.get('email')
            phone = request.form.get('phone')
            detailed_location = request.form.get('detailed_location') or request.form.get('other_location')
            national_id = request.form.get('national_id')

            username = username.strip() if username else username
            email = email.strip() if email else email

            existing_account = db.session.execute(
                text("SELECT id FROM users WHERE username = :u OR email = :e"),
                {'u': username, 'e': email}
            ).fetchone()
            if existing_account:
                flash('يوجد حساب مسجل مسبقاً بنفس اسم المستخدم أو البريد الإلكتروني. إذا كان لك حساب بالفعل فبإمكانك تسجيل الدخول مباشرة.', 'danger')
                return render_template('merchant_signUp.html', form=form)

            if national_id and not str(national_id).isdigit():
                flash('يجب أن يتكون الرقم الوطني من أرقام فقط.', 'danger')
                return render_template('merchant_signUp.html', form=form)

            nationa_num = int(str(national_id)[-9:]) if national_id else None

            if nationa_num:
                existing = db.session.execute(
                    text("SELECT id FROM retailers WHERE nationa_num = :n"),
                    {'n': nationa_num}
                ).fetchone()
                if existing:
                    flash('هذا الرقم الوطني مسجل مسبقاً. إذا كان حسابك مسجلاً بالفعل يمكنك تسجيل الدخول مباشرة.', 'danger')
                    return render_template('merchant_signUp.html', form=form)

            hashed_password = generate_password_hash(password)

            # Generate OTP and store pending registration
            otp_code = str(secrets.randbelow(900000) + 100000)
            session['pending_signup'] = {
                'role': 'retailer',
                'form_data': {
                    'username': username,
                    'email': email,
                    'phone': phone,
                    'detailed_location': detailed_location,
                    'national_id': national_id
                },
                'hashed_password': hashed_password,
                'email': email,
                'otp_code': otp_code,
                'attempts': 0,
                'expires_at': time.time() + 600  # 10 minutes
            }

            sent = send_otp_email(email, otp_code)
            if not sent:
                flash('لم يتم تجهيز إعدادات إرسال البريد بعد. رمز التحقق للتجربة هو: ' + otp_code, 'info')
            else:
                flash('تم إرسال رمز التحقق (OTP) إلى بريدك الإلكتروني. يرجى التحقق من صندوق الوارد.', 'info')
            return redirect(url_for('verify_otp'))

        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء التسجيل: {str(e)}', 'danger')
    elif request.method == 'POST':
        if form.errors:
            failed_fields = '، '.join(form[field].label.text for field in form.errors)
            flash(f'يرجى مراجعة الحقول التالية: {failed_fields}', 'danger')
        else:
            flash('يرجى التحقق من البيانات وإعادة المحاولة.', 'danger')
    return render_template('merchant_signUp.html', form=form)


def _get_pending_flow():
    """Pick the active OTP flow (signup|login). If both exist, the most recent wins."""
    pending_signup = session.get('pending_signup')
    pending_login = session.get('pending_login')
    if pending_signup and pending_login:
        if pending_signup.get('expires_at', 0) >= pending_login.get('expires_at', 0):
            return pending_signup, 'signup'
        return pending_login, 'login'
    if pending_signup:
        return pending_signup, 'signup'
    if pending_login:
        return pending_login, 'login'
    return None, None


@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    pending, mode = _get_pending_flow()
    if not pending:
        flash('لا يوجد طلب تحقق معلق. يرجى البدء من جديد.', 'danger')
        return redirect(url_for('login'))

    # state: ok / expired / blocked (5 failed attempts)
    if time.time() > pending.get('expires_at', 0):
        state = 'expired'
    elif pending.get('attempts', 0) >= 5:
        state = 'blocked'
    else:
        state = 'ok'

    masked_email = None
    if pending.get('email'):
        parts = pending['email'].split('@')
        masked_email = parts[0][:1] + '***@' + parts[1]

    if request.method == 'POST':
        submitted_otp = request.form.get('otp', '').strip()

        if state != 'ok':
            flash('انتهت صلاحية رمز التحقق أو تم تجاوز عدد المحاولات. يرجى طلب رمز جديد من الأسفل.', 'danger')
        elif submitted_otp == pending.get('otp_code'):
            if mode == 'login':
                session['user_id'] = pending['user_id']
                session['username'] = pending['username']
                session['role'] = pending['role']
                session.pop('pending_login', None)
                flash('تم تسجيل الدخول بنجاح', 'success')
                return redirect(url_for('factory_profile'))

            # mode == 'signup': create the account now that OTP is confirmed
            try:
                role = pending['role']
                form_data = pending['form_data']
                hashed_password = pending['hashed_password']
                email = pending['email']

                sql_user = text("""
                    INSERT INTO users (username, email, password, role, phone)
                    VALUES (:username, :email, :password, :role, :phone)
                    RETURNING id;
                """)
                result = db.session.execute(sql_user, {
                    'username': form_data['username'],
                    'email': email,
                    'password': hashed_password,
                    'role': role,
                    'phone': form_data['phone']
                })
                user_id = result.fetchone()[0]

                if role == 'Manufacturer':
                    sql_manufacturer = text("""
                        INSERT INTO manufacturers (user_id, commercial_register, address, have_cars, factory_name)
                        VALUES (:user_id, :commercial_register, :address, :have_cars, :factory_name);
                    """)
                    db.session.execute(sql_manufacturer, {
                        'user_id': user_id,
                        'commercial_register': form_data['commercial_register'],
                        'address': form_data['location'],
                        'have_cars': True if form_data['shipping_available'] == 'yes' else False,
                        'factory_name': form_data['factory_name']
                    })
                else:  # retailer
                    nationa_num = int(str(form_data['national_id'])[-9:]) if form_data.get('national_id') else None
                    sql_merchant = text("""
                        INSERT INTO retailers (user_id, commercial_register, shipping_address, nationa_num)
                        VALUES (:user_id, :commercial_register, :shipping_address, :nationa_num);
                    """)
                    db.session.execute(sql_merchant, {
                        'user_id': user_id,
                        'commercial_register': None,
                        'shipping_address': form_data['detailed_location'],
                        'nationa_num': nationa_num
                    })

                db.session.commit()
                session.pop('pending_signup', None)
                flash('تم تأكيد البريد الإلكتروني وإنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                msg = str(e).lower()
                if 'duplicate key' in msg or 'unique' in msg:
                    session.pop('pending_signup', None)
                    flash('استُخدم اسم المستخدم أو البريد الإلكتروني أو الرقم الوطني أثناء تأكيد الحساب. يرجى بدء التسجيل من جديد.', 'danger')
                    return redirect(url_for('login'))
                flash(f'حدث خطأ أثناء تأكيد الحساب: {str(e)}', 'danger')
        else:
            # wrong OTP -> count the attempt
            pending['attempts'] = pending.get('attempts', 0) + 1
            if mode == 'signup':
                session['pending_signup'] = pending
            else:
                session['pending_login'] = pending
            if pending['attempts'] >= 5:
                state = 'blocked'
                flash('تم بلوغ الحد الأقصى للمحاولات (5). يرجى طلب رمز جديد للمتابعة.', 'danger')
            else:
                flash(f'رمز التحقق غير صحيح. المحاولات المتبقية: {5 - pending["attempts"]}', 'danger')

    return render_template('verify_otp.html', masked_email=masked_email, mode=mode, state=state)


@app.route('/resend-otp', methods=['GET', 'POST'])
def resend_otp():
    pending, mode = _get_pending_flow()
    if not pending:
        flash('لا يوجد طلب تحقق معلق.', 'danger')
        return redirect(url_for('login'))

    # Generate a fresh OTP and reset the attempt counter
    new_otp = str(secrets.randbelow(900000) + 100000)
    pending['otp_code'] = new_otp
    pending['attempts'] = 0
    pending['expires_at'] = time.time() + 600
    if mode == 'signup':
        session['pending_signup'] = pending
    else:
        session['pending_login'] = pending

    sent = send_otp_email(pending['email'], new_otp)
    if not sent:
        flash('لم يتم تجهيز إعدادات إرسال البريد بعد. رمز التحقق للتجربة هو: ' + new_otp, 'info')
    else:
        flash('تم إرسال رمز تحقق جديد إلى بريدك الإلكتروني.', 'info')
    return redirect(url_for('verify_otp'))


@app.route('/factory/profile', methods=['GET'])
def factory_profile():
    return render_template('factoryProfile.html')


@app.route('/factory/orders', methods=['GET'])
def factory_orders():
    return render_template('orders.html')


@app.route('/factory/products', methods=['GET'])
def factory_products():
    return render_template('productManagement.html')


@app.route('/factory/reports', methods=['GET'])
def factory_reports():
    return render_template('report.html')


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='localhost', port=port, debug=app.config['DEBUG'])