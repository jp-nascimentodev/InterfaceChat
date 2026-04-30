import customtkinter as ctk
import json
import threading
from tkinter import messagebox

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ChatApp(ctk.CTk):
    def __init__(self, client_socket):
        super().__init__()
        self.client_socket = client_socket
        self.usuario_atual = None
        self.contato_labels = {}
        self._recv_lock = threading.Lock()

        self.title("Fala Aí - Projeto Chat")
        self.geometry("400x500")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._ao_fechar)

        self.tela_login()

    def _enviar_e_receber(self, dado):
        with self._recv_lock:
            self.client_socket.sendall(json.dumps(dado).encode())
            resposta = self.client_socket.recv(4096)
            return json.loads(resposta.decode())

    def _ao_fechar(self):
        if self.usuario_atual:
            try:
                self.client_socket.sendall(json.dumps({"acao": "logout", "nome": self.usuario_atual}).encode())
            except Exception:
                pass
        try:
            self.client_socket.close()
        except Exception:
            pass
        self.destroy()

    def _iniciar_polling(self):
        def _poll():
            if not self.usuario_atual:
                return
            try:
                dado = {"acao": "buscarClientes"}
                with self._recv_lock:
                    self.client_socket.sendall(json.dumps(dado).encode())
                    resposta = self.client_socket.recv(4096)
                    lista = json.loads(resposta.decode())

                for contato in lista:
                    nome = contato[0]
                    status = contato[1]
                    if nome in self.contato_labels:
                        indicador = "🟢" if status == "online" else "⚪"
                        cor = "#00FF00" if status == "online" else "#A0A0A0"
                        self.contato_labels[nome].configure(
                            text=f"{indicador} {nome}",
                            text_color=cor
                        )
            except Exception:
                pass
            self.after(5000, _poll)

        self.after(5000, _poll)

    def tela_login(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.label_titulo = ctk.CTkLabel(self, text="FALA AÍ", font=("Roboto", 32, "bold"))
        self.label_titulo.pack(pady=(60, 30))

        self.entry_user = ctk.CTkEntry(self, placeholder_text="Nome de Usuário", width=250, height=40)
        self.entry_user.pack(pady=10)

        self.entry_senha = ctk.CTkEntry(self, placeholder_text="Senha", show="*", width=250, height=40)
        self.entry_senha.pack(pady=10)

        self.btn_login = ctk.CTkButton(self, text="Entrar", width=250, height=40, font=("Roboto", 14, "bold"), command=self.fazer_login)
        self.btn_login.pack(pady=(30, 10))

        self.btn_registrar = ctk.CTkButton(self, text="Registrar", width=250, height=40, font=("Roboto", 14),
                                           fg_color="transparent", border_width=2, hover_color="#1f538d", command=self.fazer_registro)
        self.btn_registrar.pack(pady=10)

    def fazer_login(self):
        user = self.entry_user.get()
        password = self.entry_senha.get()

        if not user or not password:
            messagebox.showwarning("Aviso", "Preencha todos os campos, não deixe brechas!")
            return

        dado = {"acao": "login", "nome": user, "senha": password}
        dado_resp = self._enviar_e_receber(dado)

        if dado_resp["resposta"] == True:
            self.usuario_atual = user
            self.tela_contatos(user)
            self._iniciar_polling()
        else:
            messagebox.showerror("Erro", "Credenciais inválidas. Tenta de novo!")

    def fazer_registro(self):
        user = self.entry_user.get()
        password = self.entry_senha.get()

        if not user or not password:
            messagebox.showwarning("Aviso", "Preencha todos os campos para se registrar")
            return

        dado = {"acao": "registro", "nome": user, "senha": password}
        dado_resp = self._enviar_e_receber(dado)

        if dado_resp["resposta"] == True:
            messagebox.showinfo("Sucesso", "Registrado com sucesso! Agora use suas credenciais para entrar.")
            self.entry_senha.delete(0, 'end')
        else:
            messagebox.showerror("Erro", "Esse nome já está em uso na base. Escolha outro.")

    def tela_contatos(self, user):
        for widget in self.winfo_children():
            widget.destroy()

        self.contato_labels = {}

        frame_topo = ctk.CTkFrame(self, fg_color="transparent")
        frame_topo.pack(fill="x", pady=10, padx=20)

        ctk.CTkLabel(frame_topo, text=f"Usuario: {user}", font=("Roboto", 18, "bold")).pack(side="left")

        btn_atualizar = ctk.CTkButton(frame_topo, text="Atualizar", width=80, height=30, command=self._atualizar_status)
        btn_atualizar.pack(side="right")

        ctk.CTkLabel(self, text="Lista de Contatos", font=("Roboto", 14)).pack(pady=(10, 0))

        self.frame_lista = ctk.CTkScrollableFrame(self, width=350, height=380)
        self.frame_lista.pack(pady=10, padx=20, fill="both", expand=True)

        dado = {"acao": "buscarClientes"}
        lista_contatos = self._enviar_e_receber(dado)

        for contato in lista_contatos:
            nome_contato = contato[0]
            status_contato = contato[1]

            if nome_contato == user:
                continue

            frame_item = ctk.CTkFrame(self.frame_lista, corner_radius=5)
            frame_item.pack(fill="x", pady=5)

            indicador = "🟢" if status_contato == "online" else "⚪"
            cor_texto = "#00FF00" if status_contato == "online" else "#A0A0A0"

            label_nome = ctk.CTkLabel(frame_item, text=f"{indicador} {nome_contato}", font=("Roboto", 14, "bold"), text_color=cor_texto)
            label_nome.pack(side="left", padx=10, pady=10)

            self.contato_labels[nome_contato] = label_nome

            btn_chat = ctk.CTkButton(frame_item, text="Conversar", width=80, height=28,
                                     command=lambda c=nome_contato: self.abrir_chat(user, c))
            btn_chat.pack(side="right", padx=10)

    def _atualizar_status(self):
        if not self.usuario_atual:
            return
        try:
            dado = {"acao": "buscarClientes"}
            lista = self._enviar_e_receber(dado)

            for contato in lista:
                nome = contato[0]
                status = contato[1]
                if nome in self.contato_labels:
                    indicador = "🟢" if status == "online" else "⚪"
                    cor = "#00FF00" if status == "online" else "#A0A0A0"
                    self.contato_labels[nome].configure(
                        text=f"{indicador} {nome}",
                        text_color=cor
                    )
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao atualizar: {e}")

    def abrir_chat(self, usuario_atual, contato_alvo):
        print(f"[COMANDO] Iniciando protocolo de comunicação segura com: {contato_alvo}")