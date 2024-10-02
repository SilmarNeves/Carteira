from django.shortcuts import render
from django.db import connection
import pandas as pd

def get_movimentacao_context(request):
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
    
    df = pd.DataFrame(dados, columns=['Data', 'Operacao', 'Ativo', 'Quantidade', 'Preço'])
    df['Data'] = pd.to_datetime(df['Data'])
    df['AnoMes'] = df['Data'].dt.to_period('M')

    df['TipoOperacao'] = df['Operacao'].apply(lambda x: 'Compra' if 'COMPRA' in x else 'Venda' if 'VENDA' in x else 'Outro')
    df = df[df['TipoOperacao'].isin(['Compra', 'Venda'])]

    # Calcular o valor total das transações
    df['ValorTotal'] = df['Quantidade'] * df['Preço']

    compras_vendas = df.groupby(['AnoMes', 'TipoOperacao'])['ValorTotal'].sum().unstack().fillna(0)
    compras_vendas.columns = ['Total_de_Compras' if col == 'Compra' else 'Total_de_Vendas' for col in compras_vendas.columns]

    compras_vendas['Aportes'] = compras_vendas['Total_de_Compras'] - compras_vendas['Total_de_Vendas']

    # Arredondar valores para 2 casas decimais
    compras_vendas = compras_vendas.round(2)

    movimentacao = compras_vendas.reset_index().to_dict('records')

    return {
        'tabelas_nomes': tabelas_nomes,
        'tabela_selecionada': tabela_selecionada,
        'movimentacao': movimentacao
    }

def movimentacao_view(request):
    context = get_movimentacao_context(request)
    return render(request, 'movimentacao/movimentacao.html', context)
