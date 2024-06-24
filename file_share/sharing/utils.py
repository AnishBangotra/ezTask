import itsdangerous
from django.conf import settings
from django.core.mail import send_mail

def generate_encrypted_url(file_id):
    s = itsdangerous.URLSafeTimedSerializer(settings.SECRET_KEY)
    encrypted_token = serializer.dumps({'user_id': user_id, 'token': token})
    return encrypted_token

def send_verification_email(email, verification_url):
    subject = 'Verify your email'
    message = f'Please click the link to verify your email: {verification_url}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)

def decrypt_url(encrypted_url):
    serializer = itsdangerous.URLSafeTimedSerializer(settings.SECRET_KEY)
    try:
        data = serializer.loads(encrypted_url, max_age=3600)  # 1 hour expiration
        return data
    except itsdangerous.SignatureExpired:
        return None