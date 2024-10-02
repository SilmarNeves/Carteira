from django.shortcuts import render
from django.db import connection
from collections import defaultdict
from django.contrib.auth.decorators import login_required

@login_required
def carteira_view(request):
    # Mapeamento dos nomes das tabelas e seus respectivos expander
    tabelas_nomes = {
        "Carteira Silmar": "portfolio_silmar",
        "Carteira Mônica": "portfolio_monica",
        "Carteira Consolidada": "portfolio_consolidadas"
    }

    # Definir a tabela "Carteira Consolidada" como a opção padrão no seletor
    tabela_selecionada = request.GET.get('tabela', 'Carteira Consolidada')

    context = {
        'tabelas_nomes': tabelas_nomes,
        'tabela_selecionada': tabela_selecionada,
    }

    if tabela_selecionada in tabelas_nomes:
        tabela_nome = tabelas_nomes[tabela_selecionada]

        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {tabela_nome}")
            dados = cursor.fetchall()

        # Agrupar os dados por tipo
        dados_por_tipo = defaultdict(list)
        for linha in dados:
            tipo = linha[1]
            dados_por_tipo[tipo].append(linha)

        context['dados_por_tipo'] = dict(dados_por_tipo)

    return render(request, 'carteira/carteira.html', context)


