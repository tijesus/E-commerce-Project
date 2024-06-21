from django.urls import path

# TEST
from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, world. You're at the store index.")


app_name = 'store'

urlpatterns = [
    path('', index, name='index'),
]