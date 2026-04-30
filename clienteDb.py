import sqlite3

#Gera a conexão com o banco de dados exclusivo do usuário
def _conectar(usuario):
    return sqlite3.connect(f"historico_{usuario}.db")

#Cria a tabela de mensagens caso ainda não exista
def iniciar_banco_local(usuario):
    con = _conectar(usuario)
    cursor = con.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mensagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contato TEXT,
            tipo TEXT, 
            mensagem TEXT
        )
    """)
    con.commit()
    con.close()

#INSERE UMA NOVA MENSAGEM PARA O HISTORICO
def salvar_mensagem_local(usuario, contato, tipo, mensagem):
    con = _conectar(usuario)
    cursor = con.cursor()
    cursor.execute("INSERT INTO mensagens (contato, tipo, mensagem) VALUES (?, ?, ?)", (contato, tipo, mensagem))
    con.commit()
    con.close()

#Busca todas as mensagens trocadas com um contato 
def buscar_historico(usuario, contato):
    con = _conectar(usuario)
    cursor = con.cursor()
    resposta = cursor.execute("SELECT tipo, mensagem FROM mensagens WHERE contato = ? ORDER BY id", (contato,)).fetchall()
    con.close()
    return resposta