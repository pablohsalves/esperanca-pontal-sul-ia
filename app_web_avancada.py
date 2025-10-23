from flask import Flask, render_template, request, jsonify, session
from assistente_avancada import Hope 
import os 
import logging # Adicionar logging para depuração

# Configuração do Flask
app = Flask(__name__)
app.secret_key = 'chave_secreta_muito_forte_e_aleatoria' 
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

# Inicializa o Assistente (Hope)
assistente = Hope() 

# --- Rota Principal (index) -- MANTIDA --
@app.route('/')
def index():
    if 'user_id' not in session:
        session['user_id'] = os.urandom(16).hex() 

    if assistente.inicializado:
        saudacao = "Olá! Eu sou a Hope, sua parceira de fé da Igreja da Paz Pontal Sul. Como posso te ajudar hoje?"
    else:
        saudacao = "Bem-vindo à Hope. Estamos online, mas nosso serviço de inteligência artificial está temporariamente inoperante. Por favor, tente novamente mais tarde."
    
    return render_template('chat_interface.html', saudacao=saudacao, nome_app="HOPE")

# --- Rota API para o Chat (Chamada pelo script.js) ---
@app.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.get_json()
    pergunta = data.get('pergunta')
    
    if not pergunta:
        return jsonify({"resposta": "Por favor, digite uma mensagem."}), 400

    user_id = session.get('user_id')
    # CRÍTICO: Se por algum motivo o user_id falhar (expiração de sessão), cria um novo.
    if not user_id:
        user_id = os.urandom(16).hex()
        session['user_id'] = user_id
        logging.warning("Sessão expirada ou não encontrada. Novo user_id criado.")
        
    try:
        # A resposta_final é um dicionário {"resposta": "texto", "links": {}}
        resposta_final = assistente.chat(user_id, pergunta)
        
        # CRÍTICO: Garante que o objeto retornado seja JSON-serializável
        if isinstance(resposta_final, dict) and 'resposta' in resposta_final:
             return jsonify(resposta_final)
        else:
             logging.error(f"Retorno do assistente inválido: {resposta_final}")
             return jsonify({"resposta": "Erro interno: A IA retornou um formato inesperado."}), 500

    except Exception as e:
        logging.error(f"Erro CRÍTICO no processamento do chat_api: {e}")
        return jsonify({"resposta": f"Desculpe, ocorreu um erro no servidor ao processar a resposta. ({e})"}), 500

# --- Bloco de Execução ---
if __name__ == '__main__':
    app.run(debug=True)