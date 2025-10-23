from flask import Flask, render_template, request, jsonify, session
from assistente_avancada import Hope 
import os # CRÍTICO: Importação adicionada para corrigir o NameError

# --- Configuração do Flask ---
app = Flask(__name__)
# CRÍTICO: Define uma chave secreta para gerenciar sessões
app.secret_key = 'chave_secreta_muito_forte_e_aleatoria' 
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
# -----------------------------

# Inicializa o Assistente (Hope)
assistente = Hope() 

# --- Rota Principal ---
@app.route('/')
def index():
    # Garante que um ID de sessão único seja criado para o usuário
    if 'user_id' not in session:
        session['user_id'] = os.urandom(16).hex() 

    # CRÍTICO: Lógica para exibir mensagem de saudação (amigável ou erro)
    if assistente.inicializado:
        saudacao = "Olá! Eu sou a Esperança, sua parceira de fé da Igreja da Paz Pontal Sul. Como posso te ajudar hoje?"
    else:
        # Mensagem amigável quando a IA falha na inicialização (chave incorreta, etc.)
        saudacao = "Bem-vindo à Esperança. Estamos online, mas nosso serviço de inteligência artificial está temporariamente inoperante. Por favor, tente novamente mais tarde."
    
    return render_template('chat_interface.html', saudacao=saudacao)

# --- Rota API para o Chat (Chamada pelo script.js) ---
@app.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.get_json()
    pergunta = data.get('pergunta')
    
    if not pergunta:
        return jsonify({"resposta": "Por favor, digite uma mensagem."}), 400

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"resposta": "Erro de sessão. Por favor, recarregue a página."}), 500

    try:
        resposta_final = assistente.chat(user_id, pergunta)
        
        return jsonify(resposta_final)

    except Exception as e:
        # Erro genérico na API
        import logging
        logging.error(f"Erro inesperado na rota /api/chat: {e}")
        return jsonify({"resposta": f"Desculpe, ocorreu um erro inesperado no servidor. ({e})"}), 500

# --- Bloco de Execução ---
if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True)