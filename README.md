# InterfaceChat

Interface do Cliente
 
Interface gráfica do aplicativo de chat, construída com Python e CustomTkinter. Permite login, registro, troca de mensagens em tempo real, indicador de "digitando..." e histórico local de conversas.
 
---

## 🗂️ Estrutura do Projeto
 
```
├── cliente.py      → Ponto de entrada: abre a conexão com o servidor e inicia a janela
├── ChatApp.py      → Interface gráfica completa (telas, eventos, comunicação com o servidor)
├── clienteDb.py    → Banco de dados local SQLite para guardar o histórico de mensagens
├── menu.py         → Versão alternativa em modo terminal (sem interface gráfica)
└── historico_<usuario>.db  → Gerado automaticamente ao fazer login
```
 
---

## ▶️ Como Rodar o Cliente
 
### Pré-requisitos
 
- Python 3.8 ou superior
- Biblioteca `customtkinter` instalada:
```bash
pip install customtkinter
```
 
- O **servidor deve estar rodando** antes de iniciar o cliente (veja o README do servidor)
### Passos
 
1. Com o servidor já ativo, abra o terminal na pasta do projeto.
2. Execute:
```bash
python cliente.py
```
 
3. A janela do **CHAT** será aberta automaticamente.
> ⚠️ Se o servidor não estiver rodando, uma mensagem de erro será exibida no terminal e o programa encerrará.
 
---


## 🖥️ Telas da Interface
 
### 1. Tela de Login / Registro
 
A primeira tela que aparece ao abrir o app. Aqui você pode:
 
- **Entrar** com nome de usuário e senha já cadastrados
- **Registrar** um novo usuário diretamente pela mesma tela
### 2. Tela de Contatos
 
Após o login, você vê todos os usuários cadastrados no sistema com seu status:
 
- 🟢 **Verde** → usuário online (pode trocar mensagens em tempo real)
- ⚪ **Cinza** → usuário offline (mensagem será guardada e entregue quando ele entrar)
A lista é atualizada automaticamente a cada **5 segundos**.
 
### 3. Tela de Chat
 
Ao clicar em "Conversar" em um contato, a janela de chat é aberta:
 
- Mostra o histórico completo da conversa (salvo localmente)
- Exibe mensagens em tempo real
- Mostra o indicador **"fulano está digitando..."** quando o contato está escrevendo
- Permite enviar mensagens com o botão ou pressionando **Enter**
---
 
## 🔌 Conexão com o Servidor
 
O arquivo `cliente.py` é responsável por abrir a conexão antes de iniciar a interface:
 
```python
HOST = "127.0.0.1"
PORTA = 12345
```
 
Para conectar em outro servidor, basta alterar esses valores no `cliente.py`.
 
---
 
## 📨 Protocolo de Comunicação (lado do cliente)
 
O cliente se comunica com o servidor enviando e recebendo **JSON pelo socket TCP**. Abaixo estão todas as mensagens que o cliente envia ou recebe:
 
---
 
### 📤 Mensagens que o CLIENTE envia
 
#### Registrar usuário
```json
{
  "acao": "registro",
  "nome": "maria",
  "senha": "123456"
}
```
 
#### Fazer login
```json
{
  "acao": "login",
  "nome": "maria",
  "senha": "123456"
}
```
 
#### Buscar lista de contatos (polling a cada 5s)
```json
{ "acao": "buscarClientes" }
```
 
#### Enviar uma mensagem
```json
{
  "acao": "enviar_mensagem",
  "remetente": "maria",
  "destinatario": "joao",
  "mensagem": "Oi, João!"
}
```
 
#### Avisar que está digitando
```json
{
  "acao": "digitando",
  "remetente": "maria",
  "destinatario": "joao"
}
```
> Enviado automaticamente quando o usuário começa a digitar no campo de texto.
 
#### Avisar que parou de digitar
```json
{
  "acao": "parou_digitando",
  "remetente": "maria",
  "destinatario": "joao"
}
```
> Enviado automaticamente 2 segundos após a última tecla pressionada, ou ao enviar a mensagem.
 
#### Fazer logout
```json
{
  "acao": "logout",
  "nome": "maria"
}
```
> Enviado automaticamente ao fechar a janela.
 
---
 
### 📥 Mensagens que o CLIENTE recebe
 
#### Resposta de login ou registro
```json
{ "resposta": true, "nome": "maria" }
```
ou
```json
{ "resposta": false }
```
 
#### Lista de contatos (resposta ao buscarClientes)
```json
[
  ["maria", "online"],
  ["joao", "offline"]
]
```
 
#### Mensagem recebida de outro usuário
```json
{
  "acao": "enviar_mensagem",
  "remetente": "joao",
  "mensagem": "Oi, Maria!"
}
```
 
#### Confirmação de envio
```json
{ "acao": "confirmacao", "status": "enviado" }
```
ou, se o destinatário estiver offline:
```json
{ "acao": "confirmacao", "status": "offline" }
```
> Quando offline, o cliente exibe: `[Sistema: Destinatário offline. Mensagem guardada]`
 
#### Indicador de digitando
```json
{ "acao": "digitando", "remetente": "joao" }
```
 
#### Indicador de parou de digitar
```json
{ "acao": "parou_digitando", "remetente": "joao" }
```
 
---
 
## 🗄️ Banco de Dados Local (Histórico)
 
Cada usuário tem seu próprio arquivo de histórico gerado automaticamente no login



Como Funciona por Baixo dos Panos
 
| Recurso | Como está implementado |
|---|---|
| Recebimento de mensagens | Thread separada rodando em segundo plano (`_thread_recebimento`) |
| Atualização da interface | Método `self.after()` garante que a UI seja atualizada com segurança pela thread principal |
| Indicador "digitando..." | Timer de 2 segundos cancelado e reiniciado a cada tecla pressionada |
| Atualização de contatos | Polling automático a cada 5 segundos (`_iniciar_polling`) |
| Histórico persistente | SQLite local por usuário — independente do servidor |
 
---

##Modo Terminal
 
O arquivo `menu.py` contém uma versão mais antiga e simples do cliente, que roda direto no terminal sem interface gráfica.Foi util para testes.


