saldo = 100

while saldo > 0:
    print("\n===== CASSINO =====")
    print(f"saldo: {saldo} moedas")
    print("1 - apostar na roleta")
    print("2 - sair")

    opcao = input("escolha: ")

    if opcao == "2":
        print("valeu por jogar!")
        break

    if opcao == "1":
        aposta = int(input("quanto quer apostar? "))

        if aposta <= 0 or aposta > saldo:
            print("aposta inválida!")
            continue

        numero = int(input("escolha um número de 0 a 36: "))

        if numero < 0 or numero > 36:
            print("número inválido!")
            continue

        resultado = random.randint(0, 36)

        print(f"\na roleta girou...")
        print(f"resultado: {resultado}")

        if numero == resultado:
            premio = aposta * 35
            saldo += premio
            print(f"🎉 você ganhou {premio} moedas!")
        else:
            saldo -= aposta
            print(f"você perdeu {aposta} moedas")

    else:
        print("opção inválida!")

print("\njogo encerrado")
print(f"saldo final: {saldo} moedas")