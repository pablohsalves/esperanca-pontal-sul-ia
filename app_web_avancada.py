# app_web_avancada.py (VERSÃO PRONTA PARA DEPLOY)

from flask import Flask, request, jsonify, render_template, session
import os
import json
from assistente_avancada import ParceiroDeFeAvancado
from dotenv import load_dotenv # Importe para garantir que .env seja lido no Gunicorn

# --- Carregamento de Variáveis de Ambiente ---
# Isso garante que a chave secreta e a chave API sejam lidas
load_dotenv() 


# --- 1. CONFIGURAÇÃO INICIAL DO FLASK ---
app = Flask(__name__)
# Define a chave secreta (O Gunicorn não usará o debug, mas a chave é essencial)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'chave_secreta_super_segura_padrao_mude_isso') 

try:
    # Inicializa a assistente UMA VEZ ao iniciar o servidor
    assistente = ParceiroDeFeAvancado()
except ValueError as e:
    # Em produção, um erro de inicialização deve ser logado, mas não deve parar o Gunicorn
    print(f"ERRO CRÍTICO: Falha ao inicializar o ParceiroDeFeAvancado. {e}")
    # Podemos re-raise a exceção para que o Gunicorn saiba que houve um erro sério
    # Mas vamos deixá-lo inicializar com o assistente como None para testes de rota
    assistente = None 
    # Em um ambiente real, você faria: raise Exception(f"Falha de IA: {e}") 


# --- FUNÇÕES AUXILIARES PARA SERIALIZAÇÃO ROBUSTA ---
# ... (Mantenha as funções serialize_history exatamente como estão) ...
def serialize_history(history: list) -> list:
    """
    Converte a lista de objetos Content do Gemini em lista de dicionários (JSON serializável).
    """
    
    serialized_list = []
    for message in history:
        try:
            serialized_list.append(json.loads(message.model_dump_json()))
        except AttributeError:
            serialized_list.append(message.to_dict())
            
    return serialized_list

# --- 2. ROTAS DA APLICAÇÃO ---
# ... (Mantenha as rotas / e /api/chat exatamente como estão) ...

@app.route('/', methods=['GET'])
def index():
    # ... (código da rota index) ...
    if 'chat_history' not in session:
        print("Iniciando novo histórico vazio para o usuário.")
        session['chat_history'] = assistente.iniciar_novo_chat() 
        
    return render_template('chat_interface.html', saudacao=assistente.enviar_saudacao())

@app.route('/api/chat', methods=['POST'])
def chat():
    # Verifica se a assistente falhou na inicialização (caso de erro na chave API, etc.)
    if assistente is None:
         return jsonify({"erro": "O serviço de IA está inoperante. Verifique a chave API."}), 503

    # ... (o restante da rota chat permanece o mesmo, usando 'assistente') ...
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
# REMOVIDO: if __name__ == '__main__': app.run(debug=True)
# O Gunicorn agora executará o app.