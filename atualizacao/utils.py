import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from django.db import connection
import concurrent.futures

def copiar_dados():
    origem_path1 = "C:\\Users\\Silmar Moreno\\Desktop\\TRADERSPLAN-3.401 MONICA\\TRADERS PLAN_3.45 PRO.xlsm"
    origem_path2 = "C:\\Users\\Silmar Moreno\\Desktop\\TRADERSPLAN-3.401 SILMAR\\TRADERS PLAN_3.45 PRO.xlsm"

    df_origem1 = pd.read_excel(origem_path1, sheet_name="OPERAÇÕES", usecols="A:E")
    df_origem1 = df_origem1.iloc[1:]  # Excluindo a primeira linha
    df_origem1.columns = ['Data', 'Operacao', 'Ativo', 'Quantidade', 'Preço']

    df_origem2 = pd.read_excel(origem_path2, sheet_name="OPERAÇÕES", usecols="A:E")
    df_origem2 = df_origem2.iloc[1:]  # Excluindo a primeira linha
    df_origem2.columns = ['Data', 'Operacao', 'Ativo', 'Quantidade', 'Preço']

    return df_origem1, df_origem2

def obter_preco(ativo, data=None):
    ticker_symbol = f"{ativo}.SA"
    ticker = yf.Ticker(ticker_symbol)
    if data:
        hist = ticker.history(start=data, end=data + timedelta(days=1))
    else:
        hist = ticker.history(period="1d")
    if not hist.empty:
        return round(hist['Close'][0], 2)
    else:
        print(f"Histórico de preços não encontrado para {ticker_symbol}")
        return None

def buscar_precos(ativos):
    ativos_precos = {}
    ativos_precos_anteriores = {}

    def obter_precos(ativo):
        preco_atual = obter_preco(ativo)
        hoje = datetime.today().date()
        dia_util_anterior = hoje - timedelta(days=1 if hoje.weekday() > 0 else 3)
        preco_anterior = obter_preco(ativo, data=dia_util_anterior)
        return ativo, preco_atual, preco_anterior

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(obter_precos, ativos)
    
    for ativo, preco_atual, preco_anterior in results:
        if preco_atual is not None:
            ativos_precos[ativo] = preco_atual
        if preco_anterior is not None:
            ativos_precos_anteriores[ativo] = preco_anterior
    
    return ativos_precos, ativos_precos_anteriores

def calcular_colunas_adicionais(df, ativos_precos, ativos_precos_anteriores):
    df['Preço Atual'] = df['Ativo'].map(ativos_precos).round(2)
    df['Preço Anterior'] = df['Ativo'].map(ativos_precos_anteriores).round(2)
    df['Patrimônio Atual'] = (df['Quantidade'] * df['Preço Atual']).round(2)
    df['Ganho/Perda Hoje %'] = (((df['Preço Atual'] - df['Preço Anterior']) / df['Preço Anterior']) * 100).round(2)
    df['Ganho/Perda Hoje R$'] = ((df['Preço Atual'] - df['Preço Anterior']) * df['Quantidade']).round(2)
    df['Variação Total %'] = (((df['Preço Atual'] - df['Preço']) / df['Preço']) * 100).round(2)
    return df

def calcular_percentuais(df):
    total_por_tipo = df.groupby('Operacao')['Patrimônio Atual'].sum()
    total_geral = df['Patrimônio Atual'].sum()
    
    df['% Ativo'] = df.apply(lambda row: round((row['Patrimônio Atual'] / total_por_tipo[row['Operacao']]) * 100, 2) if total_por_tipo[row['Operacao']] != 0 else 0, axis=1)
    df['% Carteira'] = df.apply(lambda row: round((row['Patrimônio Atual'] / total_geral) * 100, 2) if total_geral != 0 else 0, axis=1)
    return df

def atualizar_transacoes_otimizado():
    df_origem1, df_origem2 = copiar_dados()
    
    for df in [df_origem1, df_origem2]:
        df['Quantidade'] = pd.to_numeric(df['Quantidade'], errors='coerce')
        df['Preço'] = pd.to_numeric(df['Preço'], errors='coerce')
    
    todos_ativos = pd.concat([df_origem1['Ativo'], df_origem2['Ativo']]).unique()
    ativos_precos, ativos_precos_anteriores = buscar_precos(todos_ativos)
    
    tabelas_transacoes = ["transacoes_silmar", "transacoes_monica", "transacoes_consolidadas"]
    dados = [df_origem2, df_origem1, pd.concat([df_origem1, df_origem2])]
    
    with connection.cursor() as cursor:
        for tabela, df in zip(tabelas_transacoes, dados):
            df = calcular_colunas_adicionais(df, ativos_precos, ativos_precos_anteriores)
            rows_to_insert = [
                [
                    row['Data'], row['Operacao'], row['Ativo'], row['Quantidade'], 
                    row['Preço Médio'], row['Preço Atual'], row['Preço Anterior'], 
                    row['Ganho/Perda Hoje %'], row['Ganho/Perda Hoje R$'], 
                    row['Patrimônio Atual'], row['% Ativo'], row['% Carteira'], row['Variação Total %']
                ]
                for _, row in df.iterrows()
            ]
            cursor.executemany(f"""
                INSERT INTO {tabela} 
                (Data, Operacao, Ativo, Quantidade, "Preço Médio", "Preço Atual", "Preço Anterior", "Ganho/Perda Hoje %", "Ganho/Perda Hoje R$", "Patrimônio Atual", "% Ativo", "% Carteira", "Variação Total %")
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, rows_to_insert)
            connection.commit()

def atualizar_cotacao_otimizado():
    tabelas_portfolio = ["portfolio_silmar", "portfolio_monica", "portfolio_consolidadas"]

    with connection.cursor() as cursor:
        for tabela in tabelas_portfolio:
            cursor.execute(f"SELECT Ativo, Quantidade, Tipo FROM {tabela}")
            ativos_info = cursor.fetchall()

            ativos_precos, ativos_precos_anteriores = buscar_precos([info[0] for info in ativos_info])

            patrimonio_por_tipo = {}
            total_geral = 0

            for ativo, quantidade, tipo in ativos_info:
                preco_atual = ativos_precos.get(ativo)
                if preco_atual is not None:
                    patrimonio_atual = round(quantidade * preco_atual, 2)
                    if tipo not in patrimonio_por_tipo:
                        patrimonio_por_tipo[tipo] = 0
                    patrimonio_por_tipo[tipo] += patrimonio_atual
                    total_geral += patrimonio_atual

            rows_to_update = []
            for ativo, quantidade, tipo in ativos_info:
                preco_atual = ativos_precos.get(ativo)
                preco_anterior = ativos_precos_anteriores.get(ativo)
                if preco_atual is not None and preco_anterior is not None:
                    patrimonio_atual = round(quantidade * preco_atual, 2)
                    ganho_perda = round(((preco_atual - preco_anterior) / preco_anterior) * 100, 2)
                    diferenca = round((preco_atual - preco_anterior) * quantidade, 2)
                    
                    percentual_ativo = round((patrimonio_atual / patrimonio_por_tipo[tipo]) * 100, 2) if patrimonio_por_tipo[tipo] else 0
                    percentual_carteira = round((patrimonio_atual / total_geral) * 100, 2) if total_geral else 0

                    cursor.execute(f"SELECT \"Preço Médio\" FROM {tabela} WHERE Ativo = %s", (ativo,))
                    preco_medio = cursor.fetchone()[0]
                    
                    variacao_total = round(((preco_atual - preco_medio) / preco_medio) * 100, 2)

                    rows_to_update.append((preco_atual, preco_anterior, ganho_perda, diferenca, patrimonio_atual, percentual_ativo, percentual_carteira, variacao_total, ativo))

            cursor.executemany(f"""
                UPDATE {tabela}
                SET "Preço Atual" = %s, "Preço Anterior" = %s, "Ganho/Perda Hoje %" = %s, "Ganho/Perda Hoje R$" = %s, 
                    "Patrimônio Atual" = %s, "% Ativo" = %s, "% Carteira" = %s, "Variação Total %" = %s
                WHERE Ativo = %s
            """, rows_to_update)

        connection.commit()
