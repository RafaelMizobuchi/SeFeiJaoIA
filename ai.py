from ollama import Client

from memoria import (
    inicializar_banco,
    salvar_mensagem,
    carregar_historico
)

client = Client(host="http://localhost:11434")

inicializar_banco()

INSTRUCOES = {
    "role": "system",
    "content": (
        "Seu nome é Jarvis. "
        "Você é um assistente pessoal de inteligência artificial "
        "desenvolvido para auxiliar o usuário em seu computador Windows. "
        "Responda sempre em português brasileiro, "
        "de maneira natural, clara e objetiva. "
        "Utilize as informações disponíveis no histórico da conversa "
        "para responder às perguntas. "
        "Você ainda não possui ferramentas para controlar o computador. "
        "Não afirme que executou ações que não realizou."
    )
}


def conversar(mensagem):

    historico = carregar_historico(10)

    mensagens = [
        INSTRUCOES,
        *historico,
        {
            "role": "user",
            "content": mensagem
        }
    ]

    resposta = client.chat(
        model="qwen3:4b-instruct",
        messages=mensagens
    )

    texto_resposta = resposta.message.content

    salvar_mensagem("user", mensagem)
    salvar_mensagem("assistant", texto_resposta)

    return texto_resposta