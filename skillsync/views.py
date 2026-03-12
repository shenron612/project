import base64
import json
from datetime import datetime

import requests
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from skillsync.forms import RegisterForm
from skillsync.models import User

def dashboard(request):
    profiles = User.objects.all().order_by('-date_joined')
    return render(request, 'dashboard.html', {
        'user':     request.user,
        'profiles': profiles,
    })


def register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'errors': {'detail': ['Invalid request.']}}, status=400)

        form = RegisterForm(data)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return JsonResponse({'success': True, 'message': f'Welcome, {user.full_name}! Your account has been created.'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    return redirect('dashboard')


def user_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'errors': {'detail': ['Invalid request.']}}, status=400)

        email    = data.get('email', '')
        password = data.get('password', '')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'success': True, 'message': f'Welcome back, {user.full_name}!'})
        else:
            return JsonResponse({'success': False, 'errors': {'detail': ['Invalid email or password.']}}, status=400)

    return redirect('dashboard')


def user_logout(request):
    logout(request)
    return redirect('dashboard')

def search_workers(request):
    query = request.GET.get('q', '').strip()
    users = []

    if query:
        users = User.objects.filter(
            Q(full_name__icontains=query) |
            Q(skills__icontains=query) |
            Q(role__icontains=query)
        )

    return JsonResponse({
        'workers': [
            {
                'id':           u.id,
                'full_name':    u.full_name,
                'role':         u.role,
                'skills':       u.skills,
                'hourly_wage':  str(u.hourly_wage) if u.hourly_wage else 'N/A',
                'hours_per_day': u.hours_per_day or 'N/A',
                'working_days': u.working_days,
            }
            for u in users
        ]
    })

def get_mpesa_token():
    consumer_key    = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    credentials     = base64.b64encode(f"{consumer_key}:{consumer_secret}".encode()).decode()
    response = requests.get(
        'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials',
        headers={'Authorization': f'Basic {credentials}'}
    )
    return response.json().get('access_token')


def get_password_and_timestamp():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    shortcode = settings.MPESA_SHORTCODE
    passkey   = settings.MPESA_PASSKEY
    raw       = f"{shortcode}{passkey}{timestamp}"
    password  = base64.b64encode(raw.encode()).decode()
    return password, timestamp

@login_required
def make_payment(request):
    worker_id = request.GET.get('worker_id')
    worker    = None
    if worker_id:
        try:
            worker = User.objects.get(id=worker_id)
        except User.DoesNotExist:
            pass
    return render(request, 'make_payment.html', {'worker': worker})


@login_required
def stk_push(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed.'}, status=405)
    try:
        data      = json.loads(request.body)
        phone     = data.get('phone', '').strip()
        amount    = data.get('amount', '').strip()
        worker_id = data.get('worker_id', '')

        if phone.startswith('0'):
            phone = '254' + phone[1:]
        elif phone.startswith('+'):
            phone = phone[1:]

        if not phone or not amount:
            return JsonResponse({'success': False, 'error': 'Phone and amount are required.'})

        token               = get_mpesa_token()
        password, timestamp = get_password_and_timestamp()

        payload = {
            'BusinessShortCode': settings.MPESA_SHORTCODE,
            'Password':          password,
            'Timestamp':         timestamp,
            'TransactionType':   'CustomerPayBillOnline',
            'Amount':            int(amount),
            'PartyA':            phone,
            'PartyB':            settings.MPESA_SHORTCODE,
            'PhoneNumber':       phone,
            'CallBackURL':       settings.MPESA_CALLBACK_URL,
            'AccountReference':  f'HireLink-{worker_id or "payment"}',
            'TransactionDesc':   'HireLink Worker Payment',
        }

        response = requests.post(
            'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest',
            json=payload,
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        )
        result = response.json()

        if result.get('ResponseCode') == '0':
            return JsonResponse({
                'success':          True,
                'message':          'STK Push sent! Check your phone to complete payment.',
                'checkout_request': result.get('CheckoutRequestID'),
            })
        else:
            return JsonResponse({'success': False, 'error': result.get('errorMessage', 'STK Push failed.')})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def mpesa_callback(request):
    if request.method == 'POST':
        try:
            data     = json.loads(request.body)
            callback = data['Body']['stkCallback']
            code     = callback.get('ResultCode')
            if code == 0:
                items   = {i['Name']: i.get('Value') for i in callback['CallbackMetadata']['Item']}
                amount  = items.get('Amount')
                receipt = items.get('MpesaReceiptNumber')
                phone   = items.get('PhoneNumber')
                print(f"✅ Payment received: KES {amount} from {phone} | Receipt: {receipt}")
            else:
                print(f"❌ Payment failed: {callback.get('ResultDesc')}")
        except Exception as e:
            print(f"Callback error: {e}")
    return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})
def about(request):
    """
    Renders the standalone About page.
    """
    return render(request, 'about.html')

def terms(request):
    return render(request, 'terms.html')

def contact(request):
    return render(request, 'contact.html')

def careers(request):
    return render(request, 'careers.html')

def privacy(request):
    return render(request, 'privacy.html')