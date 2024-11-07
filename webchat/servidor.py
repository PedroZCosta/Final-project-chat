import socket as sock
import threading

# Função para recebimento de mensagens do cliente
def recebe_dados(sock_cliente, endereco):
    nome = sock_cliente.recv(50).decode()  # Recebe o nome do cliente
    print(f"Conexão bem sucedida com {nome} via endereço: {endereco}")
    
    # Adiciona o cliente na lista com seu nome e socket
    lista_clientes.append((nome, sock_cliente))
    
    broadcast(f"{nome} entrou no chat!", sock_cliente)

    while True:
        try:
            mensagem = sock_cliente.recv(1024).decode()
            if mensagem.startswith("/"):
                # Comando Unicast: /nome para mensagem privada
                destinatario, msg = mensagem[1:].split(' ', 1)
                unicast(destinatario, msg, nome)
            elif mensagem == "/quit":
                remover(sock_cliente, nome)
                break
            else:
                broadcast(f"{nome} >> {mensagem}", sock_cliente)
        except:
            remover(sock_cliente, nome)
            break


# Função para enviar mensagem a todos os clientes conectados
def broadcast(mensagem, origem):
    for nome, cliente in lista_clientes:
        if cliente != origem:  # Evita que o remetente receba sua própria mensagem
            try:
                cliente.send(mensagem.encode())
            except:
                remover(cliente, nome)


# Função para enviar mensagem privada para um cliente específico
def unicast(destinatario, mensagem, remetente):
    for nome, cliente in lista_clientes:
        if nome == destinatario:
            try:
                cliente.send(f"{remetente} (privado) >> {mensagem}".encode())
            except:
                remover(cliente, nome)
            return
    print(f"Cliente {destinatario} não encontrado.")


# Função para remover cliente da lista e fechar a conexão
def remover(cliente, nome):
    if cliente in [c for _, c in lista_clientes]:
        lista_clientes.remove((nome, cliente))
        cliente.close()
        broadcast(f"{nome} saiu do chat.", cliente)
        print(f"{nome} foi desconectado.")


# Endereço para o servidor
HOST = '127.0.0.1'
PORTA = 9999

lista_clientes = []
sock_server = sock.socket(sock.AF_INET, sock.SOCK_STREAM)

# Tentativa de conexão do servidor
try:
    sock_server.bind((HOST, PORTA))
    sock_server.listen()
    print(f"O servidor {HOST}:{PORTA} está aguardando conexões")

    # Loop para aceitar conexões de clientes, em casso de erro mensagem e fechamento do servidor
    while True:
        try:
            sock_conn, ender = sock_server.accept()
            thread_cliente = threading.Thread(target=recebe_dados, args=[sock_conn, ender])
            thread_cliente.start()
        except Exception as e:
            print(f"Erro ao aceitar conexão: {e}")

except Exception as e:
    print(f"Erro na inicialização do servidor: {e}")
    sock_server.close()



