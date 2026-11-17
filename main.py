from ai import conversar

while True:
    mensagem = input("Você: ")

    if mensagem.lower() == "sair":
        print("Jarvis: Até logo!")
        break

    resposta = conversar(mensagem)

    print(f"Jarvis: {resposta}")