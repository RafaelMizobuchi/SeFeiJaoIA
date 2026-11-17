import json
from ollama import Client
from pydantic import BaseModel, Field
import unicodedata

client = Client(host="http://localhost:11434")

class MemoriaExtraida(BaseModel):
    categoria: str
    chave: str
    valor: str


class ResultadoExtracao(BaseModel):
    memorias: list[MemoriaExtraida] = Field(default_factory=list)

CATEGORIAS_PERMITIDAS = {
    "estudos",
    "carreira",
    "preferencias",
    "projetos"
}

def normalizar_chave(chave):

    chave = chave.strip().lower()

    chave = unicodedata.normalize("NFKD", chave)

    chave = "".join(
        caractere
        for caractere in chave
        if not unicodedata.combining(caractere)
    )

    chave = chave.replace(" ", "_")

    return chave

def validar_memorias(memorias):

    memorias_validas = []

    for memoria in memorias:

        categoria = memoria["categoria"].strip().lower()
        chave = normalizar_chave(memoria["chave"])
        valor = memoria["valor"].strip()
        chave = padronizar_chave(categoria, chave)

        if categoria not in CATEGORIAS_PERMITIDAS:
            continue

        if not chave or not valor:
            continue

        memorias_validas.append({
            "categoria": categoria,
            "chave": chave,
            "valor": valor
        })

    return memorias_validas

def padronizar_chave(categoria, chave):

    equivalencias = {
        "preferencias": {
            "linguagem_de_programacao_favorita": "linguagem_favorita",
            "linguagem_programacao_favorita": "linguagem_favorita",
            "editor_de_codigo_favorito": "editor_favorito",
            "editor_codigo_favorito": "editor_favorito",
            "ide_favorita": "editor_favorito"
        }
    }

    chaves_categoria = equivalencias.get(categoria, {})

    return chaves_categoria.get(chave, chave)

def extrair_memorias(mensagem):

    resposta = client.chat(
        model="qwen3:4b-instruct",
        messages=[
            {
                "role": "system",
                "content": (
                    "Você é um sistema de extração de memórias. "
                    "Identifique fatos duradouros explicitamente informados "
                    "pelo usuário, como estudos, preferências e objetivos. "
                    "Extraia cada fato relevante separadamente. "
                    "Não invente informações. "
                    "Não extraia perguntas ou informações hipotéticas. "
                    "Não extraia dados sensíveis. "
                    "Utilize categorias consistentes, como "
                    "'estudos', 'carreira', 'preferencias' e 'projetos'. "
                    "Retorne as informações seguindo exatamente "
                    "o esquema JSON solicitado. "
                    "Se não houver memórias, retorne uma lista vazia."
                    "Quando identificar informações sobre um projeto, "
                    "utilize uma chave específica contendo o nome do projeto. "
                    "Por exemplo: 'sentinelpy_nome', 'sentinelpy_objetivo', "
                    "'jarvis_nome' ou 'jarvis_linguagem'. "
                    "Não utilize chaves genéricas como 'nome' ou 'objetivo' "
                    "para projetos diferentes. "
                    "Extraia memórias somente quando o usuário estiver "
                    "afirmando explicitamente um fato sobre si mesmo, "
                    "suas preferências, objetivos ou projetos. "

                    "Perguntas sobre informações anteriores não devem "
                    "gerar novas memórias. "

                    "Se o usuário perguntar 'Qual é o nome do meu projeto?', "
                    "retorne uma lista vazia. "

                    "Não interprete o nome Jarvis, quando utilizado para "
                    "chamar o assistente, como o nome de um projeto. "

                    "Não transforme descrições de atividades em nomes "
                    "de projetos. "

                    "Se houver dúvida sobre a existência de um novo fato, "
                    "não extraia nenhuma memória. "
                )
            },
            {
                "role": "user",
                "content": mensagem
            }
        ],
        format=ResultadoExtracao.model_json_schema()
    )

    resultado = ResultadoExtracao.model_validate_json(
        resposta.message.content
    )

    memorias = [
        memoria.model_dump()
        for memoria in resultado.memorias
]

    return validar_memorias(memorias)

if __name__ == "__main__":

    testes = [
        ("preferencias", "linguagem_de_programacao_favorita"),
        ("preferencias", "linguagem_programacao_favorita"),
        ("preferencias", "editor_de_codigo_favorito"),
        ("preferencias", "ide_favorita"),
        ("projetos", "sentinelpy_nome")
    ]

    for categoria, chave in testes:

        resultado = padronizar_chave(categoria, chave)

        print(f"{chave} -> {resultado}")