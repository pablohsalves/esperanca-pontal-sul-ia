# app_web_avancada.py

from flask import Flask, request, jsonify, render_template, session
import os
import json 
from assistente_avancada import ParceiroDeFeAvancado


# --- 1. CONFIGURAÇÃO INICIAL DO FLASK ---
app = Flask(__name__)
# Define a chave secreta (OBRIGATÓRIA para usar 'session')
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'chave_secreta_super_segura_padrao_mude_isso') 

try:
    assistente = ParceiroDeFeAvancado()
except ValueError as e:
    print(f"ERRO CRÍTICO: Falha ao inicializar o ParceiroDeFeAvancado. {e}")
    print("O servidor será encerrado. Verifique sua chave API e o arquivo .env.")
    exit()

# --- FUNÇÕES AUXILIARES PARA SERIALIZAÇÃO ROBUSTA ---

def serialize_history(history: list) -> list:
    """
    Converte a lista de objetos Content do Gemini em lista de dicionários (JSON serializável).
    """
    
    serialized_list = []
    for message in history:
        # Usa .model_dump_json() para garantir a serialização de objetos Pydantic/Protocol Buffer
        try:
            serialized_list.append(json.loads(message.model_dump_json()))
        except AttributeError:
            # Fallback para versões mais antigas
            serialized_list.append(message.to_dict())
            
    return serialized_list


# --- 2. ROTAS DA APLICAÇÃO ---

@app.route('/', methods=['GET'])
def index():
    """
    Renderiza o template e gerencia a inicialização do histórico na sessão.
    """
    if 'chat_history' not in session:
        print("Iniciando novo histórico vazio para o usuário.")
        session['chat_history'] = assistente.iniciar_novo_chat() 
        
    return render_template('chat_interface.html', saudacao=assistente.enviar_saudacao())

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Recebe a pergunta, recupera o histórico, processa e atualiza a sessão.
    """
    
    dados = request.get_json()
    
    if not dados or 'pergunta' not in dados:
        return jsonify({"erro": "Requisição inválida. É necessário fornecer a chave 'pergunta'."}), 400

    pergunta_usuario = dados.get('pergunta')
    
    # --- 2.1. Recuperar o Histórico ---
    historico_mensagens_serializado = session.get('chat_history', []) 

    # --- 2.2. Processamento com Memória e Grounding ---
    resposta_assistente, novo_historico_objetos = assistente.obter_resposta_com_memoria(
        historico_mensagens_serializado, 
        pergunta_usuario
    )
    
    # --- 2.3. Serializar e Atualizar a Sessão ---
    session['chat_history'] = serialize_history(novo_historico_objetos)
    
    return jsonify({
        "pergunta": pergunta_usuario,
        "resposta": resposta_assistente,
        "status": "sucesso"
    })

# --- 3. EXECUÇÃO DO SERVIDOR ---
if __name__ == '__main__':
    app.run(debug=True)