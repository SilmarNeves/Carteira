from django.urls import path
from . import views

urlpatterns = [
    path('', views.atualizacao_view, name='atualizacao'),
    path('atualizar-transacoes/', views.atualizar_transacoes_view, name='atualizar_transacoes'),
    path('atualizar-cotacao/', views.atualizar_cotacao_view, name='atualizar_cotacao'),
    path('atualizar_tudo/', views.atualizar_tudo, name='atualizar_tudo'),
]

