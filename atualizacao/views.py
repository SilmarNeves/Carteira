from django.shortcuts import render, redirect
from .utils import atualizar_transacoes_otimizado, atualizar_cotacao_otimizado
from django.http import HttpResponse
import requests
from requests_html import HTMLSession
from django.http import JsonResponse

def atualizacao_view(request):
    return render(request, 'atualizacao/atualizacao.html')

def atualizar_transacoes_view(request):
    if request.method == 'POST':
        atualizar_transacoes_otimizado()
        return redirect('atualizacao')
    return render(request, 'atualizacao/atualizar_transacoes.html')

def atualizar_cotacao_view(request):
    if request.method == 'POST':
        atualizar_cotacao_otimizado()
        return redirect('atualizacao')
    return render(request, 'atualizacao/atualizar_cotacao.html')
# transacoes/views.py
def atualizar_tudo(request):
    session = HTMLSession()
    
    # Atualizar Transações
    response = session.get('http://127.0.0.1:8000/atualizar_transacoes/atualizar/')
    if response.status_code != 200:
        return JsonResponse({"success": False, "message": "Erro ao atualizar transações"}, status=500)
    
    # Gerar Portfólios
    response = session.get('http://127.0.0.1:8000/atualizar_transacoes/gerar/')
    if response.status_code != 200:
        return JsonResponse({"success": False, "message": "Erro ao gerar portfólios"}, status=500)
    
    # Acessar página de atualização de cotações
    response = session.get('http://127.0.0.1:8000/atualizacao/atualizar-cotacao/')
    if response.status_code != 200:
        return JsonResponse({"success": False, "message": "Erro ao acessar página de atualização de cotações"}, status=500)
    
    # Submeter o formulário para atualizar cotações
    form = response.html.find('form', first=True)
    if form:
        action_url = form.attrs.get('action')
        response = session.post(f'http://127.0.0.1:8000{action_url}', data={'csrfmiddlewaretoken': form.find('input[name="csrfmiddlewaretoken"]', first=True).attrs['value']})
        if response.status_code != 200:
            return JsonResponse({"success": False, "message": "Erro ao atualizar cotações"}, status=500)
    else:
        return JsonResponse({"success": False, "message": "Formulário de atualização de cotações não encontrado"}, status=500)
    
    return JsonResponse({"success": True, "message": "Atualização completa com sucesso!"})
