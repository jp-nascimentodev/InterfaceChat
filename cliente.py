from socket import AF_INET, SOCK_STREAM, socket
import json
from menu import menu, chatGeral, registrar, logar
 
#CRIANDO O SOCKET TCP DO CLIENTE
client_socket = socket(AF_INET, SOCK_STREAM)
#CLIENTE SE CONECTANDO COM SERVIDOR
client_socket.connect(("127.0.0.1", 12345))
 
print("Se conectando ao Servidor do Chat")
 
 
menu(client_socket)