import customtkinter as ctk
import json
from tkinter import messagebox

# Configuração do visual
ctk.set_appearance_mode("dark")  # Modo escuro para focar na missão
ctk.set_default_color_theme("blue") 

class ChatApp(ctk.CTk):
    def __init__(self, client_socket):
        super().__init__()
        self.client_socket = client_socket
        
        # Configurações da Janela
        self.title("Fala Aí - Projeto Chat")
        self.geometry("400x500")
        self.resizable(False, False)
        
        # Inicia direto no campo de batalha do login
        self.tela_login()

    def tela_login(self):
        # Limpa qualquer coisa que estiver na tela
        for widget in self.winfo_children():
            widget.destroy()

        self.label_titulo = ctk.CTkLabel(self, text="FALA AÍ", font=("Roboto", 32, "bold"))
        self.label_titulo.pack(pady=(60, 30))

        # Entradas de texto
        self.entry_user = ctk.CTkEntry(self, placeholder_text="Nome de Usuário", width=250, height=40)
        self.entry_user.pack(pady=10)

        self.entry_senha = ctk.CTkEntry(self, placeholder_text="Senha", show="*", width=250, height=40)
        self.entry_senha.pack(pady=10)

        # Botão de Login
        self.btn_login = ctk.CTkButton(self, text="Entrar", width=250, height=40, font=("Roboto", 14, "bold"), command=self.fazer_login)
        self.btn_login.pack(pady=(30, 10))

        # Botão de Registro (Transparente com borda)
        self.btn_registrar = ctk.CTkButton(self, text="Registrar", width=250, height=40, font=("Roboto", 14),
                                           fg_color="transparent", border_width=2, hover_color="#1f538d", command=self.fazer_registro)
        self.btn_registrar.pack(pady=10)

    def fazer_login(self):
        user = self.entry_user.get()
        password = self.entry_senha.get()

        if not user or not password:
            messagebox.showwarning("Aviso", "Preencha todos os campos, não deixe brechas!")
            return

        # Monta o pacote de dados e envia pro servidor
        dado = {"acao": "login", "nome": user, "senha": password}
        self.client_socket.sendall(json.dumps(dado).encode())
        
        # Aguarda o retorno da base
        resposta = self.client_socket.recv(1024)
        dado_resp = json.loads(resposta.decode())

        if dado_resp["resposta"] == True:
            self.tela_contatos(user) # Missão cumprida, avança pra próxima fase!
        else:
            messagebox.showerror("Erro", "Credenciais inválidas. Tenta de novo!")

    def fazer_registro(self):
        user = self.entry_user.get()
        password = self.entry_senha.get()

        if not user or not password:
            messagebox.showwarning("Aviso", "Preencha todos os campos para se registrar")
            return

        # Monta o pacote de registro
        dado = {"acao": "registro", "nome": user, "senha": password}
        self.client_socket.sendall(json.dumps(dado).encode())
        
        resposta = self.client_socket.recv(1024)
        dado_resp = json.loads(resposta.decode())

        if dado_resp["resposta"] == True:
            messagebox.showinfo("Sucesso", "Registrado com sucesso! Agora use suas credenciais para entrar.")
            self.entry_senha.delete(0, 'end') # Limpa a senha pra facilitar a vida
        else:
            messagebox.showerror("Erro", "Esse nome já está em uso na base. Escolha outro.")

    def tela_contatos(self, user):
        
        for widget in self.winfo_children():
            widget.destroy()
        
        ctk.CTkLabel(self, text=f"Bem-vindo, {user}!", font=("Roboto", 24, "bold")).pack(pady=100)
        ctk.CTkLabel(self, text="A Lista de Contatos será construída aqui.", font=("Roboto", 14)).pack()