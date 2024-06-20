import requests
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, reverse
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login as login, logout
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.contrib import messages
from django.template.loader import render_to_string
from .forms import (
    CustomUserCreationForm,
    LoginForm,
    PasswordResetForm,
    CreateNewPasswordForm)
import jwt
from config import settings
from .models import User
from .emails import verification_email_html, reset_password_email_html, successful_reset_email_html



verification_url = "http://127.0.0.1:8000/auth/verify/{}/"

password_reset_url = "http://127.0.0.1:8000/auth/create_new_password/{}/"

def send_email(user: User, text: str | None=None, url: str | None=None):
    """
    Sends emails to users.
    """
    exp_seconds = int((timezone.now() + timedelta(minutes=5)).timestamp())

    # Create the payload dictionary
    payload = {
        "user_id": user.id,
        "iss": int(timezone.now().timestamp()),
        "exp": exp_seconds,
    }
    token = jwt.encode(payload, settings.JWT_KEY, algorithm='HS256')
    return requests.post(
        url="https://api.mailgun.net/v3/mail.praiseafk.tech/messages",
        auth=("api", settings.MAILGUN_API_KEY),
        data={"from": "noreply@mail.praiseafk.tech",
              "to": user.email,
              "subject": f"Hey {user.get_full_name()}",
              "html": text.format(url.format(token) if url else text)
              },
        timeout=120)


def home(request):
    return render(request, 'authx/home.html')

def signup(request: HttpRequest) -> HttpResponse:
    """
    GET: returns a Signup page
    POST: Creates a new user with the credentials from the form
    """
    form = CustomUserCreationForm()
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            response = send_email(user, verification_email_html, verification_url)

            # if the email was sent successfully redirect to authx:verify_user
            if response.status_code == 200:
                return redirect("authx:verify_user")
        else:
            return render(request, 'authx/signup_form.html', {'form': form})
    return render(request, 'authx/signup_form.html', {'form': form})

def verify(request: HttpRequest, token: str) -> HttpResponse:
    """
    verify the token and set user.is_active to true

    If the user is already active, send the user to already_verified.html
    If the token has expired, the user can request a new one
    If the token was tampered with, return a 403 error
    """
    try:
        decoded = jwt.decode(token, settings.JWT_KEY, algorithms=['HS256'])
        decoded_user = get_object_or_404(User, id=decoded['user_id'])

        if not decoded_user.is_active:
            decoded_user.is_active = True
            decoded_user.save()
        else:
            return render(request, 'authx/already_verified.html', )
    # expired token
    except jwt.ExpiredSignatureError:
        decoded = jwt.decode(token, settings.JWT_KEY, algorithms=['HS256'], options={"verify_exp": False})

        return render(request, "authx/generate_token.html", {"uid": decoded['user_id']})
    # invalid token
    except jwt.InvalidTokenError as e:
        return HttpResponse("Permission Denied", status=403)

    return redirect("authx:login")

# TODO this is a REST API
def generate_token(request: HttpRequest, pk: int) -> JsonResponse:
    """
    if `from` in request.GET, creates new token and sends email
    for password creation
    else, creates new token and sends mail for account verification
    """
    user = get_object_or_404(User, id=pk)
    if request.GET.get('from') == "create_new_password":
        response = send_email(user, reset_password_email_html, password_reset_url)
    else:
        response = send_email(user, verification_email_html, verification_url)
    return JsonResponse(
        {'status': 200}) if response.status_code == 200 else JsonResponse({'status': 400}, status=400)

def _login(request: HttpRequest) -> HttpResponse:
    """
    GET: return a login page
    POST: logs a user in using the credentials from the form
    """
    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)

        # TODO when user is not active but tries to login
        # TODO phone error..unique error
        if user and not user.is_active:
            response = generate_token(request, user.id)
            if response.status_code == 200:
                return HttpResponse(render_to_string("authx/verify_user.html", {}))
            else:
                messages.error(request, "Something went wrong, try again later")
                return render(request, 'authx/login_form.html', {'form': form})

        if user is not None:
            login(request, user)  # login is aliased to _login
            messages.success(request, f"Welcome {user.get_full_name()}")

            # if the user is coming from a login protected view
            if request.GET.get('next', None):
                return redirect(request.GET.get('next'))
            return redirect('authx:home')
        else:
            messages.warning(request, f"Invalid email or password")

    return render(request, 'authx/login_form.html', {'form': form})


def _logout(request: HttpRequest) -> HttpResponse:
    """
    logout the signed in user
    """
    if not request.user.is_anonymous:
        logout(request)
        messages.success(request, f"You have been logged out")
    return redirect("authx:home")


def reset_password(request: HttpRequest) -> HttpResponse:
    """
    gets the user's email and sends a link to reset their password
    """
    form = PasswordResetForm(request.POST or None)
    if request.method == 'POST':
        email = request.POST['email']
        user = get_object_or_404(User, email=email)

        response = send_email(user, reset_password_email_html, password_reset_url)

        if response.status_code == 200:
            messages.success(request, f"sent successfully to {email}")
        else:
            messages.error(request, f"Something went wrong. Try again later")


    # TODO use javascript to take away the submit button
    return render(request, 'authx/password_reset_form.html', {'form': form})

def create_new_password(request, token) -> HttpResponse:
    """
    verify the token and create a new password
    """

    try:
        decoded = jwt.decode(token, settings.JWT_KEY, algorithms=['HS256'])
        decoded_user = get_object_or_404(User, id=decoded['user_id'])
        form = CreateNewPasswordForm(request.POST or None)
        if request.method == 'POST':
            if form.is_valid():
                decoded_user.set_password(form.cleaned_data['password1'])
                print(form.cleaned_data['password1'])
                decoded_user.save()
                email = decoded_user.email
                messages.success(request, f"Your password has been changed successfully")
                send_email(decoded_user, successful_reset_email_html)
                logout(request)  # clear user's current session
                return redirect("authx:login")
        return render(request, 'authx/create_new_password_form.html', {'form': form})

    except jwt.ExpiredSignatureError:
        decoded = jwt.decode(token, settings.JWT_KEY, algorithms=['HS256'], options={"verify_exp": False})
        return render(request,
                      "authx/generate_token.html",
                      {"uid": decoded['user_id'], "from": "create_new_password"})
    except jwt.InvalidTokenError as e:
        return HttpResponse("Permission Denied", status=403)
