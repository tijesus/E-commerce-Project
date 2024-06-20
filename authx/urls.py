from django.urls import path
from . import views
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView

app_name = 'authx'

urlpatterns = [
    path("", views.home, name="home"),
    path('signup/', views.signup, name='signup'),
    path('verify_user/', TemplateView.as_view(template_name='authx/verify_user.html'), name='verify_user'),
    path('verify/<str:token>/', views.verify, name='verify'),
    path('generate_token/<int:pk>/', views.generate_token, name='token_generator'),
    path('login/', views._login, name='login'),
    path("reset_password/", views.reset_password, name='reset_password'), # login required
    path("create_new_password/<str:token>/", views.create_new_password, name='create_new_password'),
    path("logout/", views._logout, name='logout'),
]