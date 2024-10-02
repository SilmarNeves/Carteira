from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('atualizar/', views.atualizar, name='atualizar'),
    path('gerar/', views.gerar, name='gerar'),
]