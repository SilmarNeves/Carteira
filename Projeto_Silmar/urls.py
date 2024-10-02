# Projeto_Silmar/urls.py

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from home.views import home_view



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),  # Home application
    path('', include('carteira.urls')),  # Inclua as URLs do aplicativo carteira
    path('login/', include('login.urls', namespace='login')),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('carteira/', include('carteira.urls')),
    path('transacoes/', include('transacoes.urls')),
    path('movimentacao/', include('movimentacao.urls')),  # Movimentação application
    path('atualizacao/', include('atualizacao.urls')),  # Atualização application
    path('atualizar_transacoes/', include('Atualizar_Transacoes.urls')),

]


   
