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
    CreateNewPasswordForm,
    AddressForm, UserChangeForm)
import jwt
from config import settings
from .models import User
from .emails import verification_email_html, reset_password_email_html, successful_reset_email_html
import uuid
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy



verification_url = "http://127.0.0.1:8000/accounts/verify/{}/"

password_reset_url = "http://127.0.0.1:8000/accounts/create_new_password/{}/"

def send_email(user: User, text: str | None=None, url: str | None=None):
    """
    Sends emails to users.
    """
    exp_seconds = int((timezone.now() + timedelta(minutes=2)).timestamp())

    # Create the payload dictionary
    payload = {
        "user_id": str(user.id),  # uuid object is not json serializable so convert to string
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

            # if the email was sent successfully redirect to account:verify_user
            if response.status_code == 200:
                return redirect("account:verify_user")
        else:
            return render(request, 'account/signup_form.html', {'form': form})
    return render(request, 'account/signup_form.html', {'form': form})

def verify(request: HttpRequest, token: str) -> HttpResponse:
    """
    verify the token and set user.is_active to true

    If the user is already active, send the user to already_verified.html
    If the token has expired, the user can request a new one
    If the token was tampered with, return a 403 error
    """
    try:
        decoded = jwt.decode(token, settings.JWT_KEY, algorithms=['HS256'])
        user_id = uuid.UUID(decoded["user_id"])   # convert id back to UUID instance
        decoded_user = get_object_or_404(User, id=user_id)

        if not decoded_user.is_active:
            decoded_user.is_active = True
            decoded_user.save()
            return redirect("account:address")
        else:
            return render(request, 'account/already_verified.html', )
    # expired token
    except jwt.ExpiredSignatureError:
        decoded = jwt.decode(token, settings.JWT_KEY, algorithms=['HS256'], options={"verify_exp": False})

        return render(request, "account/generate_token.html", {"uid": decoded['user_id']})
    # invalid token
    except jwt.InvalidTokenError as e:
        return HttpResponse("Permission Denied", status=403)

    return redirect("account:login")

# TODO this is a REST API
def generate_token(request: HttpRequest, pk: str) -> JsonResponse:
    """
    if `from` in request.GET, creates new token and sends email
    for password creation
    else, creates new token and sends mail for account verification
    """
    user_id = uuid.UUID(pk)
    user = get_object_or_404(User, id=user_id)
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
        
        try:
            _user = User.objects.get(email=email)
        except User.DoesNotExist:
            _user = None
        user = authenticate(request, email=email, password=password)

        if _user and not _user.is_active:
            response = generate_token(request, str(_user.id))
            if response.status_code == 200:
                return HttpResponse(render_to_string("account/verify_user.html", {}))
            else:
                messages.error(request, "Something went wrong, try again later")
                return render(request, 'account/login_form.html', {'form': form})

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome {user.get_full_name()}")

            # if the user is coming from a login protected view
            if request.GET.get('next', None):
                return redirect(request.GET.get('next'))
            return redirect('store:product-list')
        else:
            messages.warning(request, f"Invalid email or password")

    return render(request, 'account/login_form.html', {'form': form})


def _logout(request: HttpRequest) -> HttpResponse:
    """
    logout the signed in user
    """
    if not request.user.is_anonymous:
        logout(request)
        messages.success(request, f"You have been logged out")
    return redirect("store:product-list")


def reset_password(request: HttpRequest) -> HttpResponse:
    """
    GET: returns a form that gets the user's email
    POST: checks if the email is linked to an account and sends a reset link to that account
          raises a 404 error if the email is not linked to any account
    """
    form = PasswordResetForm(request.POST or None)
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = get_object_or_404(User, email=email)
            response = send_email(user, reset_password_email_html, password_reset_url)

            if response.status_code == 200:
                messages.success(request, f"sent successfully to {email}")
                # TODO use javascript to take away the submit button
            else:
                messages.error(request, f"Something went wrong. Try again later")
        except User.DoesNotExist:
            messages.error(request, f"{email} is not linked to any account")
    
    return render(request, 'account/password_reset_form.html', {'form': form})

def create_new_password(request, token) -> HttpResponse:
    """
    A user gets to this view using the reset link sent to their account

    GET: returns a form that takes two passwords.
    POST: It gets a token from GET and ensures the token is valid(not expired and contains the user id).
          It gets the passwords from POST and ensures that both passwords match.
          If both passwords match and the token is valid, it sets a new password for the user
          and then sends an email to alert the user that their password is changed.
          It then clears the user's session and redirects the user to the login page

    if the token is expired:
        returns "generate_token.html" so the user can generate a new token
    if the user_id is invalid:
        return permission denied
    """

    try:
        decoded = jwt.decode(token, settings.JWT_KEY, algorithms=['HS256'])
        decoded_user = get_object_or_404(User, id=decoded['user_id'])
        form = CreateNewPasswordForm(request.POST or None)
        if request.method == 'POST':
            if form.is_valid():
                decoded_user.set_password(form.cleaned_data['password1'])

                decoded_user.save()
                email = decoded_user.email
                messages.success(request, f"Your password has been changed successfully")
                send_email(decoded_user, successful_reset_email_html)
                logout(request)  # clear user's current session
                return redirect("account:login")
        return render(request, 'account/create_new_password_form.html', {'form': form})

    except jwt.ExpiredSignatureError:
        decoded = jwt.decode(token, settings.JWT_KEY, algorithms=['HS256'], options={"verify_exp": False})
        return render(request,
                      "account/generate_token.html",
                      {"uid": decoded['user_id'], "from": "create_new_password"})
    except jwt.InvalidTokenError as e:
        return HttpResponse("Permission Denied", status=403)


class CreateAddress(LoginRequiredMixin, CreateView):
    form_class = AddressForm
    context_object_name = 'form'
    template_name = 'account/address_form.html'
    success_url = reverse_lazy("store:product-list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        # if the user already has an address
        # redirect them to updateView
        try:
            if request.user.address:
                print("redirecting")
                return redirect("account:update_address")
        except User.address.RelatedObjectDoesNotExist:
            pass
        return super().get(request, *args, **kwargs)

class UpdateAddress(LoginRequiredMixin, UpdateView):
    form_class = AddressForm
    context_object_name = 'form'
    success_url = reverse_lazy("account:home")
    template_name = 'account/address_form.html'

    def get_object(self):
        # redirect anyone who doesn't have an address to create one
        if not self.request.user.address:
            return redirect("account:address")
        return self.request.user.address

class UpdateUser(LoginRequiredMixin, UpdateView):
    form_class = UserChangeForm
    template_name = 'account/userUpdate_form.html'
    success_url = reverse_lazy("store:product-list")
    context_object_name = 'form'


    def get_object(self):
        return self.request.user