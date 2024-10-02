import pandas as pd
import sqlite3

def copiar_dados():
    origem_path1 = "C:\\Users\\Silmar Moreno\\Desktop\\TRADERSPLAN-3.401 MONICA\\TRADERS PLAN_3.45 PRO.xlsm"
    origem_path2 = "C:\\Users\\Silmar Moreno\\Desktop\\TRADERSPLAN-3.401 SILMAR\\TRADERS PLAN_3.45 PRO.xlsm"

    # Ler a planilha de origem 1 (OPERAÇÕES) e excluir a primeira linha
    df_origem1 = pd.read_excel(origem_path1, sheet_name="OPERAÇÕES", usecols="A:E")
    df_origem1 = df_origem1.iloc[1:]  # Excluindo a primeira linha
    df_origem1.columns = ['Data', 'Operacao', 'Ativo', 'Quantidade', 'Preço']

    # Ler a planilha de origem 2 (OPERAÇÕES) e excluir a primeira linha
    df_origem2 = pd.read_excel(origem_path2, sheet_name="OPERAÇÕES", usecols="A:E")
    df_origem2 = df_origem2.iloc[1:]  # Excluindo a primeira linha
    df_origem2.columns = ['Data', 'Operacao', 'Ativo', 'Quantidade', 'Preço']

    database_path = r'C:\Users\Silmar Moreno\Desktop\Django-main\db.sqlite3'
    conn = sqlite3.connect(database_path)

    # Excluir as tabelas existentes, se elas já existirem
    conn.execute("DROP TABLE IF EXISTS transacoes_monica")
    conn.execute("DROP TABLE IF EXISTS transacoes_silmar")
    conn.execute("DROP TABLE IF EXISTS transacoes_consolidadas")

    # Criar a tabela "transacoes_monica" no banco de dados com coluna id autoincremento
    conn.execute("""
        CREATE TABLE transacoes_monica (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Data DATE,
            Operacao TEXT,
            Ativo TEXT,
            Quantidade INTEGER,
            Preço REAL
        )
    """)

    # Criar a tabela "transacoes_silmar" no banco de dados com coluna id autoincremento
    conn.execute("""
        CREATE TABLE transacoes_silmar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Data DATE,
            Operacao TEXT,
            Ativo TEXT,
            Quantidade INTEGER,
            Preço REAL
        )
    """)

    # Criar a tabela "transacoes_consolidadas" com coluna id autoincremento
    conn.execute("""
        CREATE TABLE transacoes_consolidadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Data DATE,
            Operacao TEXT,
            Ativo TEXT,
            Quantidade INTEGER,
            Preço REAL
        )
    """)

    # Inserir dados de origem 1 na tabela "transacoes_monica"
    df_origem1['Data'] = pd.to_datetime(df_origem1['Data']).dt.date
    for _, row in df_origem1.iterrows():
        conn.execute("INSERT INTO transacoes_monica (Data, Operacao, Ativo, Quantidade, Preço) VALUES (?, ?, ?, ?, ?)", row.tolist())

    # Inserir dados de origem 2 na tabela "transacoes_silmar"
    df_origem2['Data'] = pd.to_datetime(df_origem2['Data']).dt.date
    for _, row in df_origem2.iterrows():
        conn.execute("INSERT INTO transacoes_silmar (Data, Operacao, Ativo, Quantidade, Preço) VALUES (?, ?, ?, ?, ?)", row.tolist())

    # Inserir dados de "transacoes_monica" na tabela "transacoes_consolidadas"
    conn.execute("INSERT INTO transacoes_consolidadas (Data, Operacao, Ativo, Quantidade, Preço) SELECT Data, Operacao, Ativo, Quantidade, Preço FROM transacoes_monica")

    # Inserir dados de "transacoes_silmar" na tabela "transacoes_consolidadas"
    conn.execute("INSERT INTO transacoes_consolidadas (Data, Operacao, Ativo, Quantidade, Preço) SELECT Data, Operacao, Ativo, Quantidade, Preço FROM transacoes_silmar")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    copiar_dados()
