from socket import AF_INET, SOCK_STREAM, socket
from ChatApp import ChatApp  #

# CRIANDO O SOCKET TCP DO CLIENTE
client_socket = socket(AF_INET, SOCK_STREAM)

try:
    # CLIENTE SE CONECTANDO COM SERVIDOR
    client_socket.connect(("127.0.0.1", 12345))
    print("Conexão estabelecida. Iniciando a Interface Gráfica...")
    
    # Inicia a janela do CustomTkinter
    app = ChatApp(client_socket)
    app.mainloop() # O loop principal da interface
    
except Exception as e:
    print(f"A conexão falhou. O servidor está rodando? Erro: {e}")
finally:
    client_socket.close()