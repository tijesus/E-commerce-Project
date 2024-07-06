"""
Classes: CustomUserCreationForm()
         LoginForm()
         PasswordResetForm()
         CreateNewPasswordForm()

Validator_instances: password_regex
                     phone_regex
                     name_regex
"""

from django import forms
from .models import User, Address
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

class CustomUserCreationForm(forms.ModelForm):
    """
    User creation form
    """
    first_name = forms.CharField(label='First Name',
                                 widget=forms.TextInput(attrs={"class": "form__field"}),
                                 validators=[name_regex],
                                 max_length=150,
                                 help_text='must be all letters'
                                 )
    last_name = forms.CharField(label='Last Name',
                                widget=forms.TextInput(attrs={"class": "form__field"}),
                                validators=[name_regex],
                                max_length=150,
                                help_text='must be all letters'
                                )
    password1 = forms.CharField(label='Password',
                                widget=forms.PasswordInput(attrs={"class": "form__field"}),
                                validators=[password_regex],
                                max_length=128,
                                help_text= 'password must contain at least 8 characters(a digit, an alphabet and a symbol)')
    password2 = forms.CharField(label='Password Confirmation',
                                widget=forms.PasswordInput(attrs={"class": "form__field"}),
                                max_length=128
                                )

    class Meta:
        model = User
        fields = ("email", "phone")
        widgets = {
            "phone": forms.TextInput(attrs={'placeholder': '01234567899', 'class': 'form__field'}),
            "email": forms.EmailInput(attrs={'placeholder': 'johndoe@example.com', 'class': 'form__field'}),
        }
        labels = {
            "phone": "Phone Number",
            "email": "Email",
        }

    def clean_password2(self) -> str:
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2


    def clean_first_name(self) -> str:
        return str(self.cleaned_data.get("first_name")).capitalize()

    def clean_last_name(self) -> str:
        return str(self.cleaned_data.get("last_name")).capitalize()

    def save(self, commit=True) -> User:
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
                             widget=forms.EmailInput(attrs={"placeholder": "doe@example.com",
                                                            'class': 'form__field'}),
                             )
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={"class": "form__field"}),)

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

    def clean_password2(self) -> str:
        """
        check if password1 == password2
        """
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match", code="Invalid_password")

        return password2

class AddressForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form__field'

    def clean(self):
        super().clean()
        self.cleaned_data = {key: value.lower().capitalize() for key, value in self.cleaned_data.items()}
        return self.cleaned_data

    class Meta:
        model = Address
        exclude = ['user']


class UserChangeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form__field'
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone']