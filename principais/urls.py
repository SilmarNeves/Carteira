from django.urls import path
from . import views

app_name = 'carteira'

urlpatterns = [
    path('', views.carteira_view, name='carteira'),
]
