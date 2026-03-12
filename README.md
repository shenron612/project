# HireLink — Setup Guide

## Project Structure
```
hirelink/
├── hirelink/
│   ├── settings.py       ← Add your M-Pesa credentials here
│   ├── urls.py
│   └── wsgi.py
├── skillsync/
│   ├── models.py         ← Custom User model
│   ├── views.py          ← All views including M-Pesa
│   ├── forms.py
│   ├── admin.py
│   ├── templates/
│   │   ├── dashboard.html
│   │   └── make_payment.html
│   └── static/
│       └── css/
│           └── main.css
├── manage.py
└── requirements.txt
```

## Setup Steps

### 1. Create & activate virtual environment
```bash
python -m venv venv
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your M-Pesa credentials in hirelink/settings.py
```python
MPESA_CONSUMER_KEY    = 'your_consumer_key'
MPESA_CONSUMER_SECRET = 'your_consumer_secret'
MPESA_SHORTCODE       = '174379'
MPESA_PASSKEY         = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
MPESA_CALLBACK_URL    = 'https://your-ngrok-url.ngrok-free.dev/mpesa-callback/'
```

### 4. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create admin user
```bash
python manage.py createsuperuser
```

### 6. Start ngrok (in a separate terminal)
```bash
ngrok http 8000
```
Copy the HTTPS URL and update MPESA_CALLBACK_URL in settings.py

### 7. Run the server
```bash
python manage.py runserver
```

### 8. Visit the site
```
http://127.0.0.1:8000
```

## Features
- Register as Employer or Worker
- Login / Logout with session persistence
- Dynamic navbar (welcome message when logged in)
- Worker search by name or skill
- M-Pesa STK Push payment (Daraja sandbox)
- Admin panel at /admin/

## Sandbox Test Phone
Use `0708374149` for sandbox M-Pesa testing.
