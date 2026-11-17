import sqlite3
from pathlib import Path
import re

CAMINHO_BANCO = Path(__file__).resolve().parent / "jarvis.db"


def buscar_memorias_relevantes(pergunta, limite=5):

    memorias = buscar_memorias()

    palavras = re.findall(r"\w+", pergunta.lower())

    palavras_ignoradas = {
        "a", "o", "as", "os",
        "de", "do", "da", "dos", "das",
        "um", "uma", "qual", "quais",
        "que", "é", "em", "no", "na"
    }

    palavras = [
        palavra
        for palavra in palavras
        if palavra not in palavras_ignoradas
    ]

    resultados = []
    
    palavras_categorias = {
    "carreira": {
        "profissional", "emprego", "estágio",
        "trabalho", "vaga"
    },
    "estudos": {
        "faculdade", "curso", "estudando",
        "aprender", "estudo"
    },
    "preferencias": {
        "favorito", "favorita", "prefiro",
        "preferência"
    },
    "projetos": {
        "projeto", "projetos"
    }
}

    # Identificar os projetos conhecidos
    nomes_projetos = set()

    for memoria in memorias:

        if (
            memoria["categoria"] == "projetos"
            and memoria["chave"].endswith("_nome")
        ):
            nome = memoria["valor"].strip().lower()
            nomes_projetos.add(nome)

    # Verificar quais projetos aparecem na pergunta
    projetos_mencionados = set()

    texto_pergunta = pergunta.lower()

    for nome in nomes_projetos:

        if nome in texto_pergunta:
            projetos_mencionados.add(nome)

    # Calcular a relevância de cada memória
    for memoria in memorias:

        if memoria["categoria"] == "testes":
            continue

        texto_memoria = (
            memoria["categoria"] + " " +
            memoria["chave"] + " " +
            memoria["valor"]
        ).lower()

        pontuacao = 0

        for palavra in palavras:

            if palavra in texto_memoria:
                pontuacao += 1

                if palavra in memoria["chave"].lower():
                    pontuacao += 2

        
        palavras_associadas = palavras_categorias.get(
            memoria["categoria"],
            set()
        )

        for palavra in palavras:

            if palavra in palavras_associadas:
                pontuacao += 2
            
    
        # Bônus para projetos mencionados explicitamente
        if memoria["categoria"] == "projetos":

            for projeto in projetos_mencionados:

                if projeto in memoria["chave"].lower():
                    pontuacao += 3
                    break

        print(
            f"[DEBUG] {memoria['categoria']} | "
            f"{memoria['chave']} -> {pontuacao} pontos"
        )

        if pontuacao > 0:
            resultados.append((pontuacao, memoria))

    resultados.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return [
        memoria
        for pontuacao, memoria in resultados[:limite]
    ]
    
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
        
        cursor.execute("""
    CREATE TABLE IF NOT EXISTS memorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        categoria TEXT NOT NULL,
        chave TEXT NOT NULL,
        valor TEXT NOT NULL,
        criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
        atualizado_em TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(categoria, chave)
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
        
        
def salvar_memoria(categoria, chave, valor):

    with sqlite3.connect(CAMINHO_BANCO) as conexao:

        cursor = conexao.cursor()

        cursor.execute("""
            INSERT INTO memorias (categoria, chave, valor)
            VALUES (?, ?, ?)

            ON CONFLICT(categoria, chave)
            DO UPDATE SET
                valor = excluded.valor,
                atualizado_em = CURRENT_TIMESTAMP
        """, (categoria, chave, valor))

def buscar_memorias(categoria=None):

    with sqlite3.connect(CAMINHO_BANCO) as conexao:

        cursor = conexao.cursor()

        if categoria is None:

            cursor.execute("""
                SELECT categoria, chave, valor
                FROM memorias
                ORDER BY id
            """)

        else:

            cursor.execute("""
                SELECT categoria, chave, valor
                FROM memorias
                WHERE categoria = ?
                ORDER BY id
            """, (categoria,))

        resultados = cursor.fetchall()

    memorias = []

    for categoria, chave, valor in resultados:

        memorias.append({
            "categoria": categoria,
            "chave": chave,
            "valor": valor
        })

    return memorias

def verificar_memoria(categoria, chave, valor):

    with sqlite3.connect(CAMINHO_BANCO) as conexao:

        cursor = conexao.cursor()

        cursor.execute("""
            SELECT valor
            FROM memorias
            WHERE categoria = ? AND chave = ?
        """, (categoria, chave))

        resultado = cursor.fetchone()

    if resultado is None:
        return "nova", None

    valor_antigo = resultado[0]

    if valor_antigo.strip().casefold() == valor.strip().casefold():
        return "duplicada", valor_antigo

    return "conflito", valor_antigo

def excluir_memoria(categoria, chave):

    with sqlite3.connect(CAMINHO_BANCO) as conexao:

        cursor = conexao.cursor()

        cursor.execute("""
            DELETE FROM memorias
            WHERE categoria = ? AND chave = ?
        """, (categoria, chave))

        quantidade_excluida = cursor.rowcount

    return quantidade_excluida

if __name__ == "__main__":

    inicializar_banco()

    perguntas = [
        "Qual é a linguagem do SentinelPy?",
        "Qual é minha linguagem favorita?",
        "Qual é meu objetivo profissional?",
        "Qual é o nome do meu projeto?"
    ]

    for pergunta in perguntas:

        print(f"\n{'=' * 50}")
        print(f"PERGUNTA: {pergunta}")

        resultados = buscar_memorias_relevantes(pergunta)

        print("\nMemórias encontradas:")

        for memoria in resultados:
            print(
                f"{memoria['categoria']} | "
                f"{memoria['chave']}: "
                f"{memoria['valor']}"
            )