import json
from threading import Thread


def menu(client_socket):
    while True:
        print("-------FALA AI -------\n")
        print("1-Login")
        print("2-Registrar")
        print("3- Sair")

        opcao = input("Digite a opcao: ")

        if opcao == "1":
            logar(client_socket)
                    
        if opcao == "2":
            registrar(client_socket)

        if opcao == "3":
            print("ATE A PROXIMA")
            exit(-1)
            

def chatGeral(client_socket, user):
    while True:
        print("\n-----------------------------------")
        print("1- Clientes Onlines")
        print("2- Lista Contatos.")
        print("3- Deslogar")

        opcao = input("\nDigite a opcao: ")

        if opcao == '1' :
             ChatMensagem(client_socket, user)
        if opcao == '2':
            listaContatos(client_socket,user)
        if opcao == '3':
            menu(client_socket)

def registrar(client_socket): 
        

        


        print("---------Registro-----------")

        user = input("Digite seu nome de usuario: ")
        password = input("Digite sua senha: ")

        dado = {"acao": "registro", "nome": user, "senha": password}
        dado_json = (json.dumps(dado)).encode()
        client_socket.sendall(dado_json)
        reposta = client_socket.recv(1024)
        dado = json.loads(reposta.decode())

        if dado["resposta"] == True:
            print("Registrado com sucesso!")
        else:
             print("Usuario ja existe.")


def logar(client_socket):
        print("----------Login---------------------")

        user = input("Digite seu nome de User: ")
        password = input("Digite o sua senha: ")

        dado = {"acao": "login", "nome": user, "senha": password}
        dado_json = (json.dumps(dado)).encode()

        client_socket.sendall(dado_json)
        reposta = client_socket.recv(1024)
        dado = json.loads(reposta.decode())

        if dado["resposta"] == True:
            print(f"Bem-vindo, {dado['nome']}!")
            chatGeral(client_socket, user)
        else:
             print("error, tenta de novo")
             logar(client_socket)


def listaContatos(client_socket,user):
        client_socket.sendall(json.dumps({"acao": "buscarClientes"}).encode())
        reposta = client_socket.recv(1024)
        reposta = json.loads(reposta.decode())
        print("Cliente: ")
        for cliente in reposta:
            print(f"  Usuario: {cliente[0]}  Status: {cliente[1]}")

        print("\n------------------------")
        while True:
            opcao = input("0- Voltar: ")

            if opcao == "0":
                 chatGeral(client_socket,user)




def ChatMensagem(client_socket, user):
    dados = {"acao": "clientes_ativos"}
    client_socket.sendall(json.dumps(dados).encode())

    data = json.loads(client_socket.recv(1024).decode())

    if data["acao"] == "clientes_ativos":
        clientes_ativos = data["clientes"]

        for i, cliente in enumerate(clientes_ativos):
            print(f"{i+1}. {cliente}")
        print("0. Voltar")

        opcao = input("Com quem quer falar? ")
        if opcao == "0":
            chatGeral(client_socket, user)
            return

        destinatario = clientes_ativos[int(opcao) - 1]

        # ✅ Thread de recebimento em paralelo
        t = Thread(target=receber_mensagens, args=(client_socket, user), daemon=True)
        t.start()

        while True:
            print("\n")
            mensagem = input("")

            if not mensagem.strip(): 
               continue
            
            print(f"voce: {mensagem}")  #

            if mensagem == "/sair":
                chatGeral(client_socket, user)
                break

            dados = {
                "acao": "enviar_mensagem",
                "remetente": user,
                "destinatario": destinatario,
                "mensagem": mensagem
            }
            client_socket.sendall(json.dumps(dados).encode())

            # Aguarda só a confirmação do servidor
            conf = json.loads(client_socket.recv(1024).decode())
            if conf.get("status") == "offline":
                print(f"(Mensagem salva — {destinatario} está offline)")


def receber_mensagens(client_socket, user):
    #Roda em background, imprime mensagens que chegam
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            reposta = json.loads(data.decode())

            if reposta.get("acao") == "enviar_mensagem":
                
                print(f"\n{reposta['remetente']}: {reposta['mensagem']}")
                
        except:
            break
