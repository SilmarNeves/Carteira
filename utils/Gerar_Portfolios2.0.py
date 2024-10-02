# main.py
import sqlite3
import pandas as pd
from portfolio_functions import calculate_portfolio_position, save_portfolio_to_database

def main():
    # Conectar-se ao banco de dados
    caminho_base_de_dados = r'C:\Users\Silmar Moreno\Desktop\Django-main\db.sqlite3'
    conn = sqlite3.connect(caminho_base_de_dados)

    # Mapeamento dos nomes das tabelas
    tabelas_nomes = {
        "transacoes_consolidadas": "Carteira Consolidada",
        "transacoes_silmar": "Carteira Silmar",
        "transacoes_monica": "Carteira Mônica"
    }

    for tabela_selecionada_bd, tabela_selecionada in tabelas_nomes.items():
        print(f"Gerando a tabela de portfolio para a {tabela_selecionada}...")
        query = f"SELECT * FROM {tabela_selecionada_bd}"
        df = pd.read_sql_query(query, conn)

        # Armazena em cache os resultados da função calculate_portfolio_position
        cached_actions = calculate_portfolio_position(df, 'COMPRA AÇÃO|VENDA AÇÃO|COMPRA FII|VENDA FII|COMPRA ETF|VENDA ETF')
        df_actions = cached_actions

        # Salva o resultado no banco de dados
        save_portfolio_to_database(df_actions, caminho_base_de_dados, f'portfolio_{tabela_selecionada_bd.replace("transacoes_", "")}')

    conn.close()

if __name__ == "__main__":
    main()