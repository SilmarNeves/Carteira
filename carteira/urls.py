from django.urls import path
from .views import carteira_view, graficos_view

urlpatterns = [
    path('carteira/', carteira_view, name='carteira'),
    path('graficos/', graficos_view, name='graficos'),
    # outras rotas...
]
