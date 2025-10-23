# app_web_avancada.py - V60.7 (Com Rota Admin e Flash)

import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import uuid
from assistente_avancada import Hope, BASE_SYSTEM_INSTRUCTION, carregar_conhecimento_local # Importações CRÍTICAS

# Inicialização do Flask
app = Flask(__name__)
# CRÍTICO: Chave secreta é necessária para usar 'flash' (mensagens de sucesso/erro)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'sua_chave_secreta_padrao_muito_segura')

# Inicialização da IA (Hope)
try:
    hope = Hope()
except Exception as e:
    print(f"Erro ao inicializar a classe Hope: {e}")
    hope = None


# --- FUNÇÕES DE ROTA ---

# Rota principal (Chat)
@app.route('/')
def index():
    # Garante que todo usuário tenha uma sessão e um ID
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
        
    saudacao_inicial = "Que a graça e a paz de Deus estejam com você! Sou a Esperança, sua parceira de fé virtual. Como posso abençoá-lo(a) hoje?"
    
    return render_template('chat_interface.html', saudacao=saudacao_inicial)


# Rota de chat (API)
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    mensagem = data.get('mensagem', '')
    user_id = session.get('user_id')

    if not hope or not hope.inicializado:
        return jsonify({
            'resposta': "O assistente de IA está indisponível no momento. Por favor, tente novamente mais tarde.",
            'links': {}
        }), 200 # Retornamos 200 para que o JS exiba a mensagem amigável

    if not mensagem:
        return jsonify({'resposta': 'Por favor, digite sua mensagem.'})

    try:
        response_data = hope.chat(user_id, mensagem)
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Erro inesperado no endpoint /api/chat: {e}")
        return jsonify({
            'resposta': "Desculpe, ocorreu um erro desconhecido durante a comunicação.",
            'links': {}
        }), 200 # Retornamos 200 para que o JS exiba a mensagem amigável

# Rota de Administração de Conhecimento (Nova Rota)
@app.route('/admin/conhecimento', methods=['GET', 'POST'])
def admin_conhecimento():
    filepath = "conhecimento_esperancapontalsul.txt"
    conhecimento = ""
    
    # Processa o formulário POST (Salvar)
    if request.method == 'POST':
        novo_conhecimento = request.form.get('conhecimento')
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(novo_conhecimento)
            
            # CRÍTICO: RECARREGA a instrução do sistema após a alteração
            if hope and hope.inicializado:
                # Gera a nova instrução combinando a base com o conhecimento recarregado
                novo_contexto = carregar_conhecimento_local(filepath)
                hope.system_instruction = BASE_SYSTEM_INSTRUCTION + novo_contexto 
                
                # Opcional: Reiniciar todas as conversas ativas para garantir que o novo contexto seja usado
                hope.conversas = {}
                
            flash('Conhecimento atualizado com sucesso! Reinicie o chat para ver as mudanças.', 'success')
            return redirect(url_for('admin_conhecimento'))

        except Exception as e:
            flash(f'Erro ao salvar o arquivo: {e}', 'error')
            print(f"Erro ao salvar arquivo em /admin/conhecimento: {e}")

    # Processa o GET (Exibir)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            conhecimento = f.read()
    except FileNotFoundError:
        conhecimento = "Arquivo de conhecimento não encontrado. Comece a digitar aqui..."
    except Exception as e:
        conhecimento = f"Erro ao ler o arquivo: {e}"
    
    return render_template('admin_conhecimento.html', conhecimento=conhecimento)


# Execução do App
if __name__ == '__main__':
    # Configuração para rodar no ambiente local
    app.run(debug=True)