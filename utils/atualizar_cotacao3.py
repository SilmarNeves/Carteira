import sqlite3
import yfinance as yf
import pandas as pd

# Conectar ao banco de dados
caminho_base_de_dados = r'C:\Users\Silmar Moreno\Desktop\Django-main\db.sqlite3'
conn = sqlite3.connect(caminho_base_de_dados)

# Definir uma função para obter o preço atual do ativo
def get_current_price(asset_code):
    asset = yf.Ticker(asset_code + '.sa')
    return asset.history().tail(1)['Close'].values[0]

# Definir uma função para calcular a variação do dia do ativo
def calcular_variacao(asset_code):
    preco_atual = get_current_price(asset_code)
    preco_anterior = get_previous_close_price(asset_code)
    variacao = ((preco_atual - preco_anterior) / preco_anterior) * 100
    return variacao

# Definir uma função para obter o preço de fechamento anterior do ativo
def get_previous_close_price(asset_code):
    asset = yf.Ticker(asset_code + '.sa')
    historical_data = asset.history(period="2d")  # Fetch 2 days of historical data
    previous_close = historical_data['Close'].iloc[0]  # Close price of the previous day
    return round(previous_close, 2)


# Atualizar a tabela existente no banco de dados
def atualizar_tabela(tabela):
    # Obter os ativos e as colunas existentes na tabela
    query = f"SELECT * FROM {tabela}"
    df_tabela = pd.read_sql_query(query, conn)

    # Calcular e preencher as novas colunas
    df_tabela['Preço Atual'] = df_tabela['Ativo'].apply(get_current_price)
    df_tabela['Preço Anterior'] = df_tabela['Ativo'].apply(get_previous_close_price)
    df_tabela['Ganho/Perda Hoje %'] = (df_tabela['Quantidade'] * df_tabela['Preço Atual']) - (df_tabela['Quantidade'] * df_tabela['Preço Anterior'])
    df_tabela['Ganho/Perda Hoje R$'] = ((df_tabela['Preço Atual'] - df_tabela['Preço Médio']) / df_tabela['Preço Médio']) * 100
    df_tabela['Patrimônio Atual'] = df_tabela['Quantidade'] * df_tabela['Preço Atual']

    # Verificar se o dataframe está vazio ou se a soma do Patrimônio Atual é zero
    if df_tabela.empty or df_tabela['Patrimônio Atual'].sum() == 0:
        # Preencher % Ativo e % Carteira com um valor específico (e.g., 0 ou mensagem)
        df_tabela['% Ativo'] = 0  # ou uma mensagem informativa
        df_tabela['% Carteira'] = 0  # ou uma mensagem informativa
    else:
        df_tabela['% Ativo'] = (df_tabela['Patrimônio Atual'] / df_tabela['Patrimônio Atual'].sum()) * 100
        df_tabela['% Carteira'] = df_tabela['Patrimônio Atual'] / df_tabela['Patrimônio Atual'].sum() * 100

    # Arredondar os valores das novas colunas
    df_tabela[['Ganho/Perda Hoje R$', '% Ativo', '% Carteira']] = df_tabela[['Ganho/Perda Hoje R$', '% Ativo', '% Carteira']].apply(lambda x: x.round(2))

    # Limitar as colunas numéricas a duas casas decimais
    df_tabela = df_tabela.round(2)

    # Atualizar a tabela no banco de dados com as variações e novas colunas calculadas
    df_tabela.to_sql(tabela, conn, if_exists='replace', index=False)

# Lista de nomes das tabelas que você quer atualizar
tabelas = ["portfolio_silmar", "portfolio_monica", "portfolio_consolidadas"]

# Iterar sobre as tabelas e atualizar apenas as colunas relevantes
for tabela in tabelas:
    atualizar_tabela(tabela)

# Fechar o banco de dados
conn.close()

print("ATUALIZAÇÃO CONCLUÍDA")


