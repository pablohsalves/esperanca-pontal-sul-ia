# app_web_avancada.py - Versão V35.0 (Completo com Correção da Saudação e Classe 'Hope')

from flask import Flask, render_template, request, jsonify, session
from assistente_avancada import Hope # CRÍTICO: Usa a classe 'Hope' corrigida

# --- Configuração do Flask ---
app = Flask(__name__)
# CRÍTICO: Define uma chave secreta para gerenciar sessões (necessário para o histórico de chat)
# Em produção, use um valor mais forte e secreto.
app.secret_key = 'chave_secreta_muito_forte_e_aleatoria' 
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
# -----------------------------

# Inicializa o Assistente (Hope)
# A inicialização irá falhar se a GEMINI_API_KEY no Render for inválida.
# O objeto 'assistente' ainda será criado.
assistente = Hope() 

# --- Rota Principal ---
@app.route('/')
def index():
    # Garante que um ID de sessão único seja criado para o usuário,
    # usado para rastrear o histórico de conversas da Hope.
    if 'user_id' not in session:
        # Usa um timestamp ou UUID simples
        session['user_id'] = os.urandom(16).hex()

    # CRÍTICO: Lógica para exibir mensagem de saudação (amigável ou erro)
    if assistente.inicializado:
        # Se a IA foi inicializada com sucesso, exibe a saudação normal.
        saudacao = "Olá! Eu sou a Esperança, sua parceira de fé da Igreja da Paz Pontal Sul. Como posso te ajudar hoje?"
    else:
        # Se a IA falhou (Erro da Chave/Render), exibe uma mensagem amigável para o usuário.
        saudacao = "Bem-vindo à Esperança. Estamos online, mas nosso serviço de inteligência artificial está temporariamente inoperante. Por favor, tente novamente mais tarde."
    
    # Renderiza o template HTML e passa a mensagem de saudação.
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
        # Chama o método 'chat' do objeto Hope
        # Este método retorna a resposta da IA ou a mensagem de erro da IA se inoperante.
        resposta_final = assistente.chat(user_id, pergunta)
        
        # O retorno já está formatado como um dicionário (JSON-like)
        return jsonify(resposta_final)

    except Exception as e:
        # Erro genérico na API
        logging.error(f"Erro inesperado na rota /api/chat: {e}")
        return jsonify({"resposta": f"Desculpe, ocorreu um erro inesperado no servidor. ({e})"}), 500

# --- Bloco de Execução ---
if __name__ == '__main__':
    # Nota: Em ambiente de produção (Render), o Gunicorn executa o app.
    # Esta seção é apenas para teste local.
    import os
    import logging
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True)