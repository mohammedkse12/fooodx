import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

def send_otp_email(to_email, otp_code):
    """
    Sends an OTP verification email to the user.
    Returns True if the email was sent via SMTP.
    Returns False if SMTP is not configured or sending failed (console fallback only).
    """
    server = current_app.config.get("MAIL_SERVER")
    port = current_app.config.get("MAIL_PORT", 587)
    use_tls = current_app.config.get("MAIL_USE_TLS", True)
    username = current_app.config.get("MAIL_USERNAME")
    password = current_app.config.get("MAIL_PASSWORD")
    sender = current_app.config.get("MAIL_DEFAULT_SENDER", "no-reply@foodx.com")

    subject = "رمز التحقق الخاص بك في منصة FoodX"
    body = f"""
    مرحباً بك في منصة FoodX،
    
    رمز التحقق الخاص بك لتأكيد عملية التسجيل هو:
    
    {otp_code}
    
    هذا الرمز صالح لمدة 10 دقائق فقط. يرجى عدم مشاركة هذا الرمز مع أي شخص.
    
    مع تحيات إدارة منصة FoodX
    """

    # Always log/print OTP for development and console fallback
    print("=" * 60)
    print(f"[FOODX OTP SERVICE] Sending OTP to {to_email}")
    print(f"OTP CODE: {otp_code}")
    print("=" * 60)

    if not username or not password or not server:
        print("[FOODX OTP SERVICE] SMTP not configured. Using console-only fallback.")
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        if port == 465:
            # SSL
            smtp = smtplib.SMTP_SSL(server, port, timeout=10)
        else:
            smtp = smtplib.SMTP(server, port, timeout=10)
            if use_tls:
                smtp.starttls()

        smtp.login(username, password)
        smtp.sendmail(sender, [to_email], msg.as_string())
        smtp.quit()
        return True
    except Exception as e:
        print(f"[FOODX OTP SERVICE] Failed to send email via SMTP: {e}. Falling back to console.")
        return False
