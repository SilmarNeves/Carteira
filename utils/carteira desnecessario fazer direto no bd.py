import sqlite3
import pandas as pd
import yfinance as yf
import streamlit as st 

def calcular_posicao_na_carteira():
    st.title("POSIÇÃO NA CARTEIRA - Controle Investimentos")

    # Conectar ao banco de dados
    caminho_base_de_dados = r'C:\Users\Silmar Moreno\Desktop\Django-main\db.sqlite3'
    conn = sqlite3.connect(caminho_base_de_dados)

    # Mapeamento dos nomes das tabelas e seus respectivos expander
    tabelas_nomes = {
        "Carteira Silmar": "portfolio_silmar",
        "Carteira Mônica": "portfolio_monica",
        "Carteira Consolidada": "portfolio_consolidadas"
    }

    # Definir a tabela "Carteira Consolidada" como a opção padrão no seletor
    tabela_selecionada = st.selectbox("Selecione a tabela:", list(tabelas_nomes.keys()), index=2)

    if tabela_selecionada:
        # Calcular valores de Ganho/Perda Hoje % e percentual para Ações
        acao_df = mostrar_dados(conn, tabelas_nomes[tabela_selecionada], "Ação")
        if acao_df is not None and not acao_df.empty:
            total_patrimonio_acoes, total_ganho_perda_acoes = calcular_ganho_perda(acao_df)
            # Mostrar dados para Ações
            with st.expander(f"Visualizar {tabelas_nomes[tabela_selecionada]} - Ações: Total Ganho/Perda Hoje % no dia (Ações): R$ {total_ganho_perda_acoes:.2f}"):
                st.dataframe(acao_df)

        # Calcular valores de Ganho/Perda Hoje % e percentual para FII's
        fii_df = mostrar_dados(conn, tabelas_nomes[tabela_selecionada], "FII")
        if fii_df is not None and not fii_df.empty:
            total_patrimonio_fiis, total_ganho_perda_fiis = calcular_ganho_perda(fii_df)
            # Mostrar dados para FII's
            with st.expander(f"Visualizar {tabelas_nomes[tabela_selecionada]} - FII's: Total Ganho/Perda Hoje % no dia (FII's): R$ {total_ganho_perda_fiis:.2f}"):
                st.dataframe(fii_df)

        # Calcular valores de Ganho/Perda Hoje % e percentual para ETF's
        etf_df = mostrar_dados(conn, tabelas_nomes[tabela_selecionada], "ETF")
        if etf_df is not None and not etf_df.empty:
            total_patrimonio_etfs, total_ganho_perda_etfs = calcular_ganho_perda(etf_df)
            # Mostrar dados para ETF's
            with st.expander(f"Visualizar {tabelas_nomes[tabela_selecionada]} - ETF's: Total Ganho/Perda Hoje % no dia (ETF's): R$ {total_ganho_perda_etfs:.2f}"):
                st.dataframe(etf_df)

        # Inicializar variáveis de patrimônio e Ganho/Perda Hoje % para ETF's
        total_patrimonio_etfs = 0
        total_ganho_perda_etfs = 0

        # Somar patrimônio total (ações + FII's + ETF's)
        total_patrimonio_total = total_patrimonio_acoes + total_patrimonio_fiis + total_patrimonio_etfs
        # Somar Ganho/Perda Hoje % total (ações + FII's + ETF's)
        total_ganho_perda_geral = total_ganho_perda_acoes + total_ganho_perda_fiis + total_ganho_perda_etfs
        
        st.write(f"<span style='font-size: 24px; color: green;'>Patrimônio Total Consolidado: R$ {total_patrimonio_total:,.2f}</span>", unsafe_allow_html=True)
        if total_ganho_perda_geral >= 0:
            cor = "green"
        else:
            cor = "red"
        total_ganho_perda_geral_formatado = "{:,.2f}".format(total_ganho_perda_geral)
        st.write(
            f"<span style='font-size: 24px; color: {cor};'>Valor de Ganho/Perda Hoje % no Dia: R$ {total_ganho_perda_geral_formatado}</span>",
            unsafe_allow_html=True,
            style=dict(
                font_size="24px",
            ),
        )
        # Calcula o percentual de Ganho/Perda Hoje % entre Valor de Ganho/Perda Hoje % no Dia e Valor Total Geral
        if total_patrimonio_total != 0:
            percentual_ganho_perda = (total_ganho_perda_geral / total_patrimonio_total) * 100
        else:
            percentual_ganho_perda = 0

        # Exibe os resultados utilizando formatação HTML para estilização
        st.write(f"<span style='font-size: 24px; color: blue;'>Ganho/Perda Hoje % %: {percentual_ganho_perda:.2f}%</span>", unsafe_allow_html=True)
          
    
def mostrar_dados(conn, tabela, tipo):
    # Consultar dados do banco de dados
    query = f"SELECT * FROM {tabela} WHERE Tipo='{tipo}'"
    df = pd.read_sql_query(query, conn)

    # Verificar se há resultados
    if df.empty:
        st.info(f"Nenhum {tipo} encontrado na carteira {tabela}.")
        return None
    else:
        return df

def calcular_ganho_perda(df):
    # Imprimir o DataFrame para verificar seu conteúdo
    print(df)
    
    # Calcular o total de Ganho/Perda Hoje % e o patrimônio total
    total_ganho_perda = df['Ganho/Perda Hoje %'].sum()
    total_patrimonio = df['Patrimônio Atual'].sum()

    return total_patrimonio, total_ganho_perda
