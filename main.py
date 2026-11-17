from ai import conversar
from memoria import (
    salvar_memoria,
    verificar_memoria,
    buscar_memorias,
    excluir_memoria
)

while True:

    mensagem = input("Você: ")

    if mensagem.lower() == "sair":
        print("Jarvis: Até logo!")
        break

    # Verificar comandos especiais
    if mensagem.strip().lower() == "/memorias":

        memorias = buscar_memorias()

        if not memorias:
            print("Jarvis: Não tenho memórias registradas.")

        else:
            print("Jarvis: Estas são as memórias registradas:")

            for memoria in memorias:

                if memoria["categoria"] == "testes":
                    continue

                print(
                    f"- {memoria['categoria']} | "
                    f"{memoria['chave']}: "
                    f"{memoria['valor']}"
                )

        continue

    if mensagem.strip().lower() == "/esquecer":

        categoria = input("Categoria: ").strip()
        chave = input("Chave: ").strip()

        memorias = buscar_memorias(categoria)

        memoria_encontrada = None

        for memoria in memorias:

            if memoria["chave"] == chave:
                memoria_encontrada = memoria
                break

        if memoria_encontrada is None:
            print("Jarvis: Não encontrei essa memória.")
            continue

        print(
            f"Jarvis: Encontrei a memória: "
            f"{memoria_encontrada['categoria']} | "
            f"{memoria_encontrada['chave']}: "
            f"{memoria_encontrada['valor']}"
        )

        confirmacao = input(
            "Deseja realmente excluir esta memória? (s/n): "
        ).strip().lower()

        if confirmacao == "s":

            quantidade = excluir_memoria(categoria, chave)

            if quantidade == 1:
                print("Jarvis: Memória excluída com sucesso.")
            else:
                print("Jarvis: Nenhuma memória foi excluída.")

        else:
            print("Jarvis: Exclusão cancelada.")

        continue

    # Somente mensagens comuns chegam aqui
    resposta, memorias = conversar(mensagem)

    print(f"Jarvis: {resposta}")

    if memorias:

        for memoria in memorias:

            categoria = memoria["categoria"]
            chave = memoria["chave"]
            valor = memoria["valor"]

            estado, valor_antigo = verificar_memoria(
                categoria,
                chave,
                valor
            )

            if estado == "duplicada":
                continue

            print("\nJarvis identificou uma possível memória:")
            print(f"Categoria: {categoria}")
            print(f"Chave: {chave}")
            print(f"Valor: {valor}")

            if estado == "nova":

                confirmacao = input(
                    "\nDeseja salvar esta memória? (s/n): "
                ).strip().lower()

            elif estado == "conflito":

                print(f"\nValor armazenado: {valor_antigo}")
                print(f"Novo valor: {valor}")

                confirmacao = input(
                    "\nDeseja substituir a memória anterior? (s/n): "
                ).strip().lower()

            else:
                continue

            if confirmacao == "s":

                salvar_memoria(categoria, chave, valor)

                print("Memória salva com sucesso!")

            else:
                print("Memória não alterada.")