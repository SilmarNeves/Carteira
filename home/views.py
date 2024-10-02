from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from carteira.views import get_carteira_context
from movimentacao.views import get_movimentacao_context
from transacoes.views import get_transacoes_context

@login_required
def home_view(request):
    carteira_context = get_carteira_context(request)
    movimentacao_context = get_movimentacao_context(request)
    transacoes_context = get_transacoes_context(request)
    context = {**carteira_context, **movimentacao_context, **transacoes_context}
    return render(request, 'home/home.html', context)
