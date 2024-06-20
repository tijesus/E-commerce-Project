from django import forms
from .models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

password_regex = RegexValidator(
        r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
        message="Password must contain at least 8 characters(a digit, an alphabet and a symbol)",
        code="Invalid_password"

    )

name_regex = RegexValidator(
    r'^[A-Za-z]+$',
    message="Name must be all letters",
    code="Invalid_name"
)

phone_regex = RegexValidator(
        r'^\d{10}$',
        message="Phone number must contain 10 numbers",
        code="Invalid_phone"
        )
class CustomUserCreationForm(forms.ModelForm):
    first_name = forms.CharField(label='First Name',
                                 widget=forms.TextInput,
                                 validators=[name_regex],
                                 max_length=150
                                 )
    last_name = forms.CharField(label='Last Name',
                                widget=forms.TextInput,
                                validators=[name_regex],
                                max_length=150
                                )
    phone = forms.CharField(max_length=10,
                            widget=forms.TextInput(attrs={'placeholder': '0123456789'}),
                            validators=[phone_regex],
                            label='Phone Number')
    password1 = forms.CharField(label='Password',
                                widget=forms.PasswordInput,
                                validators=[password_regex],
                                max_length=128)
    password2 = forms.CharField(label='Password confirmation',
                                widget=forms.PasswordInput,
                                max_length=128
                                )

    class Meta:
        model = User
        fields = ("email",)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = User(
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            phone=self.cleaned_data['phone'],
            email=self.cleaned_data['email']
        )
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    """
    login form
    """
    email = forms.EmailField(label='Email',
                             widget=forms.EmailInput(attrs={"placeholder": "doe@example.com"}),
                             )
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

class PasswordResetForm(LoginForm):
    """
    password reset form
    """
    password = None

class CreateNewPasswordForm(forms.Form):
    """
    create new password form
    """
    password1 = forms.CharField(label='Password',
                                widget=forms.PasswordInput,
                                max_length=128)
    password2 = forms.CharField(label='Password confirmation',
                                widget=forms.PasswordInput,
                                validators=[password_regex],
                                max_length=128)

    def clean_password2(self):
        """
        check if password1 == password2
        """
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match", code="Invalid_password")

        return password2