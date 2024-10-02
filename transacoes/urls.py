from django.urls import path
from .views import transacoes_view

urlpatterns = [
    path('', transacoes_view, name='transacoes'),
]
