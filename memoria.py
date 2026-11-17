import sqlite3
from pathlib import Path

CAMINHO_BANCO = Path(__file__).resolve().parent / "jarvis.db"


def inicializar_banco():

    with sqlite3.connect(CAMINHO_BANCO) as conexao:

        cursor = conexao.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mensagens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                criado_em TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
def salvar_mensagem(role, content):

    with sqlite3.connect(CAMINHO_BANCO) as conexao:

        cursor = conexao.cursor()

        cursor.execute("""
            INSERT INTO mensagens (role, content)
            VALUES (?, ?)
        """, (role, content))
        
def carregar_historico(limite=10):

    with sqlite3.connect(CAMINHO_BANCO) as conexao:

        cursor = conexao.cursor()

        cursor.execute("""
            SELECT role, content
            FROM mensagens
            ORDER BY id DESC
            LIMIT ?
        """, (limite,))

        mensagens = cursor.fetchall()

    historico = []

    for role, content in reversed(mensagens):

        historico.append({
            "role": role,
            "content": content
        })

    return historico
        
if __name__ == "__main__":

    inicializar_banco()

    historico = carregar_historico()

    print("Histórico recuperado do banco de dados:\n")

    for mensagem in historico:
        print(f"{mensagem['role']}: {mensagem['content']}")