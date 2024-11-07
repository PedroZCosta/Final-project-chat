import socket as sock
import threading

# IP e PORTA do servidor ao qual queremos nos conectar
HOST = '127.0.0.1' # Endereço do servidor
PORTA = 9999 # Porta do servidor de sockets
socket_cliente = sock.socket(sock.AF_INET, sock.SOCK_STREAM)

socket_cliente.connect((HOST, PORTA))
print(5 * "-" + " CHAT INICIADO " + "-" * 5)

# Informar o nome
nome = input("Informe seu nome para entrar no chat: ")
socket_cliente.sendall(nome.encode())

# Função para receber mensagens do servidor
def receber_mensagens():
    while True:
        try:
            mensagem = socket_cliente.recv(1024).decode()
            if not mensagem:
                print("Conexão encerrada pelo servidor.")
                break
            print(mensagem)
        except:
            print("Erro ao receber mensagem. Conexão encerrada.")
            socket_cliente.close()
            break

# Thread para receber mensagens
thread_receber = threading.Thread(target=receber_mensagens)
thread_receber.start()

# Loop de envio de mensagens
while True:
    mensagem = input(">")
    if mensagem.lower() == "/quit":
        socket_cliente.sendall(mensagem.encode())
        print("Você saiu do chat.")
        socket_cliente.close()
        break
    # Envia a mensagem codificada
    socket_cliente.sendall(mensagem.encode())