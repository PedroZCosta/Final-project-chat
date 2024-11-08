from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Mapeamento entre session id (sid) e nome de usuário
clients = {}

@app.route('/')
def index():
    return render_template('index.html')

# Rota para ir para a página do chat
@app.route('/chat')
def chat():
    username = request.args.get('username')
    return render_template('chat.html', username=username)

# Atualizar e emitir a lista de usuários para todos
def atualizar_lista_usuarios():
    user_list = list(clients.values())
    socketio.emit('update_user_list', user_list)

# Evento quando o usuário entra no chat
@socketio.on('join')
def handle_join(data):
    username = data['username']
    client_ip = request.remote_addr # Coleta o IP do usuário
    client_port = request.environ.get('REMOTE_PORT', 'Desconhecida') # Coleta a Porta do usuário
    clients[request.sid] = username  # Adiciona o usuário ao dicionário
    print(f'{username} entrou no chat! IP: {client_ip}, Porta: {client_port}') 
    emit('message', {'msg': f"{username} entrou no chat!"}, broadcast=True, include_self=False)
    atualizar_lista_usuarios()  # Envia a lista atualizada a todos

# Evento quando o usuário sai do chat
@socketio.on('disconnect')
def handle_disconnect():
    username = clients.get(request.sid, "Unknown")
    if username:
        del clients[request.sid]  # Remove o usuário do dicionário
        emit('message', {'msg': f"{username} saiu do chat!"}, broadcast=True, include_self=False)
        atualizar_lista_usuarios()  # Envia a lista atualizada a todos

# Evento de envio de mensagem pública
@socketio.on('message')
def handle_message(data):
    sid = request.sid  # Obtém o SID do remetente
    username = data['username']
    msg = data['msg'].strip()  # Remove espaços em branco


    emit('message', {'msg': f"{username}: {msg}"}, broadcast=True, include_self=False)


# Evento de envio de mensagem privada
@socketio.on('private_message')
def handle_private_message(data):
    sender = data['username']
    recipient_name = data['recipient']
    msg = data['msg']

    # Busca o `sid` do destinatário
    recipient_sid = None
    for sid, name in clients.items():
        if name == recipient_name:
            recipient_sid = sid
            break

    # Enviar mensagem privada para o destinatário
    if recipient_sid:
        # Envia a mensagem para o destinatário sem reenvio ao remetente
        emit('message', {'msg': f"(Privado de {sender}): {msg}"}, room=recipient_sid)
        # Envia uma confirmação para o remetente de que a mensagem foi enviada
        emit('message', {'msg': f"(Privado para {recipient_name}): {msg}"}, room=request.sid, include_self=False)
    else:
        # Notifica o remetente que o destinatário não foi encontrado
        emit('message', {'msg': f"Usuário {recipient_name} não encontrado."}, room=request.sid)

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=5000, debug=True)
