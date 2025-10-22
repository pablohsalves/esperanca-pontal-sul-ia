# app_web_avancada.py

from flask import Flask, request, jsonify, render_template, session
import os
import json
from assistente_avancada import ParceiroDeFeAvancado
from dotenv import load_dotenv

# --- Carregamento de Variáveis de Ambiente ---
# Isso é essencial para o Render carregar as chaves secretas e API
load_dotenv() 


# --- 1. CONFIGURAÇÃO INICIAL DO FLASK ---
app = Flask(__name__)
# A chave secreta é carregada do ambiente (Render) ou usa o padrão para segurança
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'chave_secreta_super_segura_padrao_mude_isso') 

try:
    # Inicializa a assistente UMA VEZ ao iniciar o servidor
    assistente = ParceiroDeFeAvancado()
except ValueError as e:
    print(f"ERRO CRÍTICO: Falha ao inicializar o ParceiroDeFeAvancado. {e}")
    assistente = None 
    # Em produção, um erro de inicialização deve ser logado, mas não deve parar o Gunicorn


# --- FUNÇÃO AUXILIAR PARA SERIALIZAÇÃO (MEMÓRIA) ---
# Necessário para salvar o histórico de objetos do Gemini na sessão (que usa JSON)
def serialize_history(history: list) -> list:
    """
    Converte a lista de objetos Content do Gemini em lista de dicionários (JSON serializável).
    """
    # A verificação de tipo ajuda a lidar com diferentes estruturas de objeto do SDK
    serialized_list = []
    for message in history:
        try:
            # Tenta usar o model_dump_json (Pydantic/SDK mais novo)
            serialized_list.append(json.loads(message.model_dump_json()))
        except AttributeError:
            # Fallback (para compatibilidade ou outros objetos)
            serialized_list.append(message.to_dict())
            
    return serialized_list


# --- 2. ROTAS DA APLICAÇÃO ---

@app.route('/', methods=['GET'])
def index():
    # Inicializa ou recupera o histórico de chat da sessão
    if 'chat_history' not in session:
        print("Iniciando novo histórico vazio para o usuário.")
        # Cria um histórico com a mensagem inicial (saudação)
        if assistente:
             session['chat_history'] = assistente.iniciar_novo_chat() 
        else:
             session['chat_history'] = []
            
    # A saudação é usada para preencher a primeira mensagem no HTML
    return render_template('chat_interface.html', saudacao=assistente.enviar_saudacao() if assistente else "Serviço de IA Indisponível.")

@app.route('/api/chat', methods=['POST'])
def chat():
    # Verifica se a assistente falhou na inicialização (erro na chave API, etc.)
    if assistente is None:
         return jsonify({"erro": "O serviço de IA está inoperante. Verifique a chave API."}), 503

    dados = request.get_json()
    
    if not dados or 'pergunta' not in dados:
        return jsonify({"erro": "Requisição inválida. É necessário fornecer a chave 'pergunta'."}), 400

    pergunta_usuario = dados.get('pergunta')
    
    # --- 2.1. Recuperar o Histórico ---
    # Se a sessão expirou ou não existe, usa um histórico vazio
    historico_mensagens_serializado = session.get('chat_history', []) 

    # --- 2.2. Processamento com Memória e Grounding ---
    resposta_assistente, novo_historico_objetos = assistente.obter_resposta_com_memoria(
        historico_mensagens_serializado, 
        pergunta_usuario
    )
    
    # --- 2.3. Serializar e Atualizar a Sessão ---
    # Salva o novo histórico (incluindo a pergunta e a resposta) na sessão
    session['chat_history'] = serialize_history(novo_historico_objetos)
    
    return jsonify({
        "pergunta": pergunta_usuario,
        "resposta": resposta_assistente,
        "status": "sucesso"
    })

# --- 3. EXECUÇÃO DO SERVIDOR ---
# Em produção (Render), o Gunicorn executa o 'app'. A linha abaixo é ignorada.
# if __name__ == '__main__':
#     app.run(debug=True)