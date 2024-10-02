# portfolio_functions.py
import sqlite3
import pandas as pd
import numpy as np

def calculate_portfolio_position(df, asset_type):
    df_asset = df[df['Operacao'].str.contains(asset_type, case=False)]

    # Ordenar as transações por data
    df_asset = df_asset.sort_values(by='Data')

    asset_info = {}  # Usaremos um dicionário para armazenar informações sobre cada ativo

    for index, row in df_asset.iterrows():
        date = row['Data']
        asset = row['Ativo']
        quantity = row['Quantidade'] if 'COMPRA' in row['Operacao'] else -row['Quantidade']
        price = row['Preço']

        if 'AÇÃO' in row['Operacao']:
            asset_type = 'Ação'
        elif 'FII' in row['Operacao']:
            asset_type = 'FII'
        elif 'ETF' in row['Operacao']:
            asset_type = 'ETF'
        else:
            asset_type = 'Desconhecido'

        if asset not in asset_info:
            asset_info[asset] = {
                'records': [],
                'cum_shares': 0,
                'avg_price_weight': np.nan,
                'type': asset_type,
            }

        asset_info[asset]['records'].append({
            'date': date,
            'quantity': quantity,
            'price': price,
        })

    assets = []
    asset_types = []
    avg_prices = []
    total_quantities = []

    for asset, info in asset_info.items():
        records = info['records']

        position_shares = 0
        shares_cost = 0
        avg_price_weight = np.nan

        for record in records:
            position_shares += record['quantity']
            shares_cost += record['price'] * record['quantity']

            if position_shares == 0:
                avg_price_weight = 0
            elif avg_price_weight is np.nan:
                avg_price_weight = record['price']
            elif record['quantity'] < 0:
                pass  # Manter o preço médio anterior para vendas
            else:
                avg_price_weight = (avg_price_weight * info['cum_shares'] + record['price'] * record['quantity']) / position_shares

            info['cum_shares'] = position_shares
            info['avg_price_weight'] = avg_price_weight

        if position_shares > 0:
            assets.append(asset)
            asset_types.append(info['type'])
            avg_prices.append(avg_price_weight)
            total_quantities.append(position_shares)

    df_result = pd.DataFrame({
        'Ativo': assets,
        'Tipo': asset_types,
        'Preço Médio': avg_prices,
        'Quantidade': total_quantities,
    })

    return df_result

def save_portfolio_to_database(df_result, database_path, table_name):
    conn = sqlite3.connect(database_path)

    # Verifica se a tabela já existe, se não existir, cria a tabela
    conn.execute(f'DROP TABLE IF EXISTS {table_name}')
    conn.execute(f'''CREATE TABLE {table_name} 
                (Ativo TEXT, Tipo TEXT, Quantidade INTEGER, "Preço Médio" REAL, "Preço Atual" REAL, "Preço Anterior" REAL, "Ganho/Perda Hoje %" REAL)''')
    df_result.to_sql(table_name, conn, if_exists='append', index=False)

    # Remove os registros existentes na tabela
    conn.execute(f'DELETE FROM {table_name}')

    # Insere os registros no banco de dados
    df_result.to_sql(table_name, conn, if_exists='append', index=False)

    # Fecha a conexão com o banco de dados
    conn.close()