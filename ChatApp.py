import customtkinter as ctk
import json
import threading
from tkinter import messagebox
from clienteDb import iniciar_banco_local, salvar_mensagem_local, buscar_historico

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ChatApp(ctk.CTk):
    def __init__(self, client_socket):
        super().__init__()
        self.client_socket = client_socket
        self.usuario_atual = None
        self.contato_labels = {}
        self.contato_alvo_atual = None 
        self.aguardando_login = False
        self.aguardando_registro = False

        self.title("Fala Aí - Projeto Chat")
        self.geometry("400x500")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._ao_fechar)

        threading.Thread(target=self._thread_recebimento, daemon=True).start()
        self.tela_login()

    def _ao_fechar(self):
        if self.usuario_atual:
            try:
                self.client_socket.sendall(json.dumps({"acao": "logout", "nome": self.usuario_atual}).encode())
            except Exception:
                pass
        self.client_socket.close()
        self.destroy()

    def _carregar_historico_na_tela(self, contato):
        """Busca o histórico no cliente_db e injeta na interface"""
        historico = buscar_historico(self.usuario_atual, contato)
        for tipo, msg in historico:
            if tipo == 'enviada':
                self._inserir_mensagem_na_tela(f"Você: {msg}")
            else:
                self._inserir_mensagem_na_tela(f"{contato}: {msg}")

    # ==========================================
    # LÓGICA DE RECEPÇÃO ASSÍNCRONA
    # ==========================================
    def _thread_recebimento(self):
        while True:
            try:
                data = self.client_socket.recv(4096)
                if not data:
                    break
                pacote = json.loads(data.decode())
                self.after(0, self._processar_pacote, pacote)
            except Exception as e:
                print(f"Desconectado do servidor: {e}")
                break

    def _processar_pacote(self, pacote):
        if isinstance(pacote, list):
            self._atualizar_lista_contatos_ui(pacote)
            return

        if pacote.get("acao") == "enviar_mensagem":
            remetente = pacote.get("remetente")
            mensagem = pacote.get("mensagem")
            
            salvar_mensagem_local(self.usuario_atual, remetente, "recebida", mensagem)
            
            if self.contato_alvo_atual == remetente:
                self._inserir_mensagem_na_tela(f"{remetente}: {mensagem}")
            return

        if pacote.get("acao") == "confirmacao":
            if pacote.get("status") == "offline":
                self._inserir_mensagem_na_tela("[Sistema: Destinatário offline. Mensagem guardada]")
            return

        if "resposta" in pacote:
            if self.aguardando_login:
                self.aguardando_login = False
                if pacote["resposta"] == True:
                    self.usuario_atual = pacote.get("nome", self.entry_user.get())
                    iniciar_banco_local(self.usuario_atual) 
                    self.tela_contatos(self.usuario_atual)
                    self._iniciar_polling()
                else:
                    messagebox.showerror("Erro", "Credenciais inválidas.")
            
            elif self.aguardando_registro:
                self.aguardando_registro = False
                if pacote["resposta"] == True:
                    messagebox.showinfo("Sucesso", "Registrado com sucesso! Faça login.")
                    self.entry_senha.delete(0, 'end')
                else:
                    messagebox.showerror("Erro", "Esse nome já está em uso.")
            return

    # ==========================================
    # LÓGICA DE ENVIO E ATUALIZAÇÃO
    # ==========================================
    def fazer_login(self):
        user = self.entry_user.get()
        password = self.entry_senha.get()
        if not user or not password: return

        self.aguardando_login = True
        dado = {"acao": "login", "nome": user, "senha": password}
        self.client_socket.sendall(json.dumps(dado).encode())

    def fazer_registro(self):
        user = self.entry_user.get()
        password = self.entry_senha.get()
        if not user or not password: return

        self.aguardando_registro = True
        dado = {"acao": "registro", "nome": user, "senha": password}
        self.client_socket.sendall(json.dumps(dado).encode())

    def _iniciar_polling(self):
        def _poll():
            if not self.usuario_atual: return
            try:
                dado = {"acao": "buscarClientes"}
                self.client_socket.sendall(json.dumps(dado).encode())
            except Exception:
                pass
            self.after(5000, _poll)
        self.after(0, _poll)

    def _atualizar_lista_contatos_ui(self, lista_contatos):
        if not hasattr(self, 'frame_lista') or not self.frame_lista.winfo_exists():
            return

        for widget in self.frame_lista.winfo_children():
            widget.destroy()
        
        self.contato_labels.clear()

        for contato in lista_contatos:
            nome = contato[0]
            status = contato[1]
            
            if nome == self.usuario_atual:
                continue

            frame_item = ctk.CTkFrame(self.frame_lista, corner_radius=5)
            frame_item.pack(fill="x", pady=5)

            indicador = "🟢" if status == "online" else "⚪"
            cor = "#00FF00" if status == "online" else "#A0A0A0"

            label_nome = ctk.CTkLabel(frame_item, text=f"{indicador} {nome}", font=("Roboto", 14, "bold"), text_color=cor)
            label_nome.pack(side="left", padx=10, pady=10)

            self.contato_labels[nome] = label_nome

            btn_chat = ctk.CTkButton(frame_item, text="Conversar", width=80, height=28,
                                     command=lambda c=nome: self.abrir_chat(self.usuario_atual, c))
            btn_chat.pack(side="right", padx=10)

    # ==========================================
    # CONSTRUÇÃO DAS TELAS DA INTERFACE
    # ==========================================
    def tela_login(self):
        for widget in self.winfo_children(): widget.destroy()

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

    def tela_contatos(self, user):
        for widget in self.winfo_children(): widget.destroy()
        
        self.contato_labels = {}
        self.contato_alvo_atual = None

        frame_topo = ctk.CTkFrame(self, fg_color="transparent")
        frame_topo.pack(fill="x", pady=10, padx=20)
        ctk.CTkLabel(frame_topo, text=f"Usuário: {user}", font=("Roboto", 18, "bold")).pack(side="left")

        ctk.CTkButton(frame_topo, text="Atualizar", width=80, height=30, 
                      command=lambda: self.client_socket.sendall(json.dumps({"acao": "buscarClientes"}).encode())).pack(side="right")

        ctk.CTkLabel(self, text="Lista de Contatos", font=("Roboto", 14)).pack(pady=(10, 0))

        self.frame_lista = ctk.CTkScrollableFrame(self, width=350, height=380)
        self.frame_lista.pack(pady=10, padx=20, fill="both", expand=True)

    def abrir_chat(self, usuario_atual, contato_alvo):
        self.contato_alvo_atual = contato_alvo

        for widget in self.winfo_children(): widget.destroy()

        frame_topo = ctk.CTkFrame(self, fg_color="transparent")
        frame_topo.pack(fill="x", pady=10, padx=20)

        ctk.CTkButton(frame_topo, text="< Voltar", width=60, height=30, fg_color="#555555", 
                      hover_color="#333333", command=lambda: self.tela_contatos(self.usuario_atual)).pack(side="left")
        ctk.CTkLabel(frame_topo, text=f"Chat: {contato_alvo}", font=("Roboto", 18, "bold")).pack(side="left", padx=20)

        self.caixa_mensagens = ctk.CTkTextbox(self, width=350, height=320, state="disabled", wrap="word")
        self.caixa_mensagens.pack(pady=10, padx=20, fill="both", expand=True)

        frame_base = ctk.CTkFrame(self, fg_color="transparent")
        frame_base.pack(fill="x", pady=(0, 10), padx=20)

        self.entry_msg = ctk.CTkEntry(frame_base, placeholder_text="Mensagem...", width=260, height=40)
        self.entry_msg.pack(side="left", padx=(0, 10))
        self.entry_msg.bind("<Return>", lambda event: self._enviar_mensagem_chat(contato_alvo))

        ctk.CTkButton(frame_base, text="Enviar", width=80, height=40, command=lambda: self._enviar_mensagem_chat(contato_alvo)).pack(side="right")

        self._carregar_historico_na_tela(contato_alvo)

    def _inserir_mensagem_na_tela(self, texto):
        if hasattr(self, 'caixa_mensagens') and self.caixa_mensagens.winfo_exists():
            self.caixa_mensagens.configure(state="normal")
            self.caixa_mensagens.insert("end", texto + "\n")
            self.caixa_mensagens.see("end")
            self.caixa_mensagens.configure(state="disabled")

    def _enviar_mensagem_chat(self, destinatario):
        mensagem = self.entry_msg.get()
        if not mensagem.strip(): return

        salvar_mensagem_local(self.usuario_atual, destinatario, "enviada", mensagem)

        self._inserir_mensagem_na_tela(f"Você: {mensagem}")
        self.entry_msg.delete(0, 'end')

        dado = {
            "acao": "enviar_mensagem",
            "remetente": self.usuario_atual,
            "destinatario": destinatario,
            "mensagem": mensagem
        }
        self.client_socket.sendall(json.dumps(dado).encode())