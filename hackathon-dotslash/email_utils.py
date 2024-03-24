from flask_mail import Mail, Message
import random
import string
import smtplib

mail = Mail()

def initialize_mail(app):
    mail.init_app(app)

import smtplib
from email.message import EmailMessage
import random
import string

def send_otp_email(email, mail_sender, mail_password):
    try:
        otp = ''.join(random.choices(string.digits, k=6))
        msg = EmailMessage()
        msg['Subject'] = 'OTP for Email Verification'
        msg['From'] = mail_sender
        msg['To'] = email
        msg.set_content(f'Here is the OTP to verify your email: {otp}')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(mail_sender, mail_password)
            smtp.send_message(msg)

        return otp
    except Exception as e:
        print(f"Failed to send OTP email: {e}")
        return None





    
def verify_otp2(entered_otp, generated_otp):
    return entered_otp == generated_otp
