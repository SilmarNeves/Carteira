from django.shortcuts import render
from django.db import connection
from collections import defaultdict
from django.contrib.auth.decorators import login_required

def get_carteira_context(request):
    tabelas_nomes = {
        "Carteira Consolidada": "portfolio_consolidadas",
        "Carteira Silmar": "portfolio_silmar",
        "Carteira Mônica": "portfolio_monica"
    }

    tabela_selecionada = request.GET.get('tabela', 'Carteira Consolidada')

    context = {
        'tabelas_nomes': tabelas_nomes,
        'tabela_selecionada': tabela_selecionada,
    }

    tabela_nome = tabelas_nomes.get(tabela_selecionada, 'portfolio_consolidadas')

    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {tabela_nome}")
        dados = cursor.fetchall()

    dados_por_tipo = defaultdict(list)
    totais = defaultdict(float)
    ativos_acoes = defaultdict(float)
    ativos_fiis = defaultdict(float)
    
    patrimonio_atual_total = 0
    patrimonio_anterior_total = 0
    patrimonio_atual_fii = 0
    patrimonio_anterior_fii = 0
    patrimonio_atual_acao = 0
    patrimonio_anterior_acao = 0

    for linha in dados:
        tipo = linha[1]  # Tipo
        dados_por_tipo[tipo].append(linha)
        patrimonio_atual = linha[9]  # Patrimônio Atual
        patrimonio_anterior = linha[2] * linha[6]  # Quantidade * Preço Anterior
        totais[tipo] += patrimonio_atual
        
        patrimonio_atual_total += patrimonio_atual
        patrimonio_anterior_total += patrimonio_anterior

        if tipo == 'Ação':
            ativos_acoes[linha[0]] += patrimonio_atual  # Ativo
            patrimonio_atual_acao += patrimonio_atual
            patrimonio_anterior_acao += patrimonio_anterior
        elif tipo == 'FII':
            ativos_fiis[linha[0]] += patrimonio_atual  # Ativo
            patrimonio_atual_fii += patrimonio_atual
            patrimonio_anterior_fii += patrimonio_anterior

    total_geral = sum(totais.values())
    totais['Total Geral'] = total_geral

    # Calcular variações
    variacao_fii = ((patrimonio_atual_fii / patrimonio_anterior_fii) - 1) * 100 if patrimonio_anterior_fii else 0
    variacao_acao = ((patrimonio_atual_acao / patrimonio_anterior_acao) - 1) * 100 if patrimonio_anterior_acao else 0
    variacao_total = ((patrimonio_atual_total / patrimonio_anterior_total) - 1) * 100 if patrimonio_anterior_total else 0

    # Calcular variação absoluta
    variacao_absoluta_fii = patrimonio_atual_fii - patrimonio_anterior_fii
    variacao_absoluta_acao = patrimonio_atual_acao - patrimonio_anterior_acao
    variacao_absoluta_total = patrimonio_atual_total - patrimonio_anterior_total

    context['dados_por_tipo'] = dict(dados_por_tipo)
    context['totais'] = dict(totais)
    context['variacoes'] = {
        'FII': {'percentual': variacao_fii, 'absoluta': variacao_absoluta_fii},
        'Ação': {'percentual': variacao_acao, 'absoluta': variacao_absoluta_acao},
        'Total Geral': {'percentual': variacao_total, 'absoluta': variacao_absoluta_total}
    }
    
    # Preparar dados para os gráficos
    labels_tipos = list(totais.keys())
    labels_tipos.remove('Total Geral')
    data_tipos = [totais[tipo] for tipo in labels_tipos]

    labels_acoes = list(ativos_acoes.keys())
    data_acoes = [ativos_acoes[ativo] for ativo in labels_acoes]

    labels_fiis = list(ativos_fiis.keys())
    data_fiis = [ativos_fiis[ativo] for ativo in labels_fiis]

    context['grafico_tipos_labels'] = labels_tipos
    context['grafico_tipos_data'] = data_tipos
    context['grafico_acoes_labels'] = labels_acoes
    context['grafico_acoes_data'] = data_acoes
    context['grafico_fiis_labels'] = labels_fiis
    context['grafico_fiis_data'] = data_fiis

    return context

@login_required
def carteira_view(request):
    context = get_carteira_context(request)
    return render(request, 'carteira/carteira.html', context)

@login_required
def graficos_view(request):
    context = get_carteira_context(request)
    return render(request, 'carteira/graficos.html', context)
