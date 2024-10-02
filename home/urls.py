from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'home'

urlpatterns = [
    path('', login_required(views.home_view), name='home'),
]

