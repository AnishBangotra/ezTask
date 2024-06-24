# Production steps
## settings.py:
### Ensure DEBUG is set to False.
### Set ALLOWED_HOSTS to include your production domain.
### Configure your database settings for the production database.
### Set up email backend settings for production.
### Use environment variables for sensitive information.
```
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = False

ALLOWED_HOSTS = ['yourdomain.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')

SECRET_KEY = os.getenv('SECRET_KEY')
```
### Collect Static Files
```
python manage.py collectstatic
```
## Set Up the Production Server
### Choose a Hosting Provider
### Options include DigitalOcean, AWS, Heroku, and others.
### Install Server Software
### Nginx: As a web server and reverse proxy.
### Gunicorn: As a WSGI HTTP server for running your Django application.
### PostgreSQL: As your production database.
```
# Update packages and install necessary software
sudo apt update && sudo apt upgrade -y
sudo apt install nginx python3-pip python3-dev libpq-dev postgresql postgresql-contrib
sudo apt install build-essential libssl-dev libffi-dev python3-setuptools

# Install and configure virtualenv
pip3 install virtualenv
```
## Set Up PostgreSQL Database
```
# Switch to postgres user
sudo -i -u postgres

# Open PostgreSQL prompt
psql

# Create database and user
CREATE DATABASE yourdbname;
CREATE USER yourdbuser WITH PASSWORD 'yourdbpassword';

# Modify user roles
ALTER ROLE yourdbuser SET client_encoding TO 'utf8';
ALTER ROLE yourdbuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE yourdbuser SET timezone TO 'UTC';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE yourdbname TO yourdbuser;

# Exit PostgreSQL prompt
\q

# Exit postgres user
exit
```
## Deploy Your Django Application
### Set Up Virtual Environment and Install Dependencies

```
# Navigate to your project directory
cd /path/to/your/project

# Create virtual environment
virtualenv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```
## Set Up Gunicorn
### Create a Gunicorn systemd service file.
```
sudo nano /etc/systemd/system/gunicorn.service
```
### Add the following content:
```
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=youruser
Group=www-data
WorkingDirectory=/path/to/your/project
ExecStart=/path/to/your/project/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/path/to/your/project/gunicorn.sock yourproject.wsgi:application

[Install]
WantedBy=multi-user.target
```
### Start and enable the Gunicorn service.
```
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```
## Configure Nginx
### Create an Nginx server block configuration.
```
sudo nano /etc/nginx/sites-available/yourproject

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /path/to/your/project;
    }

    location /media/ {
        root /path/to/your/project;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/path/to/your/project/gunicorn.sock;
    }
}
```
### Enable the configuration by creating a symlink.
### Test Nginx configuration and restart the service.
### Set Up Firewall (Optional but recommended)

```
sudo ln -s /etc/nginx/sites-available/yourproject /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
sudo ufw allow 'Nginx Full'
```

## Secure Your Application
### Set Up HTTPS
### Use Certbot to obtain and install a Let's Encrypt SSL certificate

```
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## Monitor and Maintain
### Set up monitoring for your server.
### Regularly back up your database.
### Keep your system and dependencies up to date.


