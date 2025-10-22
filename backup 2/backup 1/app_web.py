# app_web.py

from flask import Flask, request, jsonify
from assistente import ParceiroDeFe

# 1. Configuração Inicial do Flask
app = Flask(__name__)
# Inicializa a nossa assistente uma única vez quando o servidor inicia
assistente = ParceiroDeFe()

# 2. Definição da Rota Principal (Endpoint)
# Usaremos uma rota simples para enviar e receber dados via POST
@app.route('/chat', methods=['POST'])
def chat():
    """
    Função que recebe a requisição (pergunta) e retorna a resposta da assistente.
    """
    
    # 2.1. Documentação: Recebe os dados JSON da requisição.
    dados = request.get_json()
    
    # Validação simples: verifica se a chave 'pergunta' está no corpo da requisição
    if not dados or 'pergunta' not in dados:
        # Se a requisição for inválida, retorna um erro 400 (Bad Request)
        return jsonify({"erro": "Requisição inválida. É necessário fornecer a chave 'pergunta'."}), 400

    # 2.2. Lógica: Pega a pergunta do usuário
    pergunta_usuario = dados.get('pergunta')
    
    # 2.3. Processamento: Envia a pergunta para a nossa assistente
    resposta_assistente = assistente.obter_resposta(pergunta_usuario)
    
    # 2.4. Saída: Retorna a resposta em formato JSON
    return jsonify({
        "pergunta": pergunta_usuario,
        "resposta": resposta_assistente,
        "status": "sucesso"
    })

# 3. Rota para Teste (Opcional, mas útil)
@app.route('/', methods=['GET'])
def home():
    """Rota para verificar se o servidor está funcionando."""
    return assistente.enviar_saudacao()

# 4. Bloco de Execução do Servidor
if __name__ == '__main__':
    # Roda o servidor web do Flask. 
    # debug=True é ótimo para desenvolvimento, pois reinicia o servidor automaticamente em caso de mudanças.
    app.run(debug=True)