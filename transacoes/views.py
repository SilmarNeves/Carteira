from django.shortcuts import render
from django.db import connection
import pandas as pd

def get_transacoes_context(request):
    tabelas_nomes = {
        'transacoes_consolidadas': 'Consolidadas',
        'transacoes_silmar': 'Silmar',
        'transacoes_monica': 'Monica'
    }

    tabela_selecionada = request.GET.get('tabela', 'transacoes_consolidadas')
    
    if tabela_selecionada not in tabelas_nomes:
        tabela_selecionada = 'transacoes_consolidadas'
    
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT Data, Operacao, Ativo, Quantidade, Preço FROM {tabela_selecionada}")
        dados = cursor.fetchall()
    
    if dados:
        df = pd.DataFrame(dados, columns=['Data', 'Operacao', 'Ativo', 'Quantidade', 'Preço'])
        df['Data'] = pd.to_datetime(df['Data'])
        transacoes = df.to_dict('records')
    else:
        transacoes = []

    return {
        'tabelas_nomes': tabelas_nomes,
        'tabela_selecionada': tabela_selecionada,
        'dados': transacoes
    }

def transacoes_view(request):
    context = get_transacoes_context(request)
    return render(request, 'transacoes/transacoes.html', context)
