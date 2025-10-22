# app_web_avancada.py - ARQUIVO PRINCIPAL DO FLASK

from flask import Flask, render_template, request, session, jsonify, redirect, url_for
import json
import os
from assistente_avancada import ParceiroDeFeAvancado
from dotenv import load_dotenv

# --- Carregamento de Variáveis de Ambiente ---
# Isso é essencial para o Render carregar as chaves secretas e API
load_dotenv() 

# --- 1. CONFIGURAÇÃO INICIAL DO FLASK ---
app = Flask(__name__)
# A chave secreta é carregada do ambiente (Render) ou usa o padrão para segurança
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'sua_chave_secreta_padrao_muito_segura') 

try:
    # Inicializa a assistente UMA VEZ ao iniciar o servidor
    assistente = ParceiroDeFeAvancado()
except ValueError as e:
    print(f"ERRO CRÍTICO: Falha ao inicializar o ParceiroDeFeAvancado. {e}")


# ----------------------------------------------------
# CONFIGURAÇÕES E FUNÇÕES DO PAINEL ADMIN
# ----------------------------------------------------

CONHECIMENTO_PATH = 'conhecimento_esperancapontalsul.txt'

def ler_conhecimento_atual():
    """Lê o conteúdo atual do arquivo de conhecimento."""
    # Garante que o caminho é absoluto, crucial no ambiente Render
    caminho_completo = os.path.join(os.path.dirname(os.path.abspath(__file__)), CONHECIMENTO_PATH)
    try:
        with open(caminho_completo, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        # Retorna o texto inicial se o arquivo não for encontrado (para evitar quebrar o admin)
        return """
# conhecimento_esperancapontalsul.txt

Pastor Líder: Pastor Daniel Rodrigues
Localização da Sede: Rua A-4, Quadra 44, Lote 17, Setor Garavelo, Aparecida de Goiânia - GO.
Horário de Cultos: Domingos às 19:00h e Terças-feiras (Culto da Vitória) às 19:30h.
Missão da Igreja: Levar a mensagem de Jesus Cristo a todas as famílias e formar discípulos que impactem sua comunidade com amor e esperança.
Visão Principal: Uma comunidade vibrante, centrada na Palavra de Deus (a Bíblia Sagrada), focada em missões urbanas e no discipulado.
Base Doutrinária: Ênfase na Bíblia Sagrada como a única regra de fé e prática, o Batismo nas águas por imersão, a Santa Ceia e o Poder do Espírito Santo.
Livro de Referência: A Bíblia Sagrada é o principal livro de estudo e ensino.

# NOVOS DADOS PARA LINKS CLICÁVEIS (Atualize-os no Painel Admin!):
Contato WhatsApp: 5562998765432
Instagram Oficial: @esperancapontalsul
Link do Google Maps (Endereço): https://maps.app.goo.gl/exemplo
"""
    except Exception as e:
        return f"ERRO ao ler o arquivo: {e}"

def salvar_novo_conhecimento(novo_conteudo):
    """Sobrescreve o arquivo de conhecimento com o novo conteúdo."""
    caminho_completo = os.path.join(os.path.dirname(os.path.abspath(__file__)), CONHECIMENTO_PATH)
    try:
        with open(caminho_completo, 'w', encoding='utf-8') as f:
            f.write(novo_conteudo)
        return True
    except Exception as e:
        print(f"ERRO ao salvar o arquivo: {e}")
        return False

# ----------------------------------------------------
# ROTAS DO FLASK
# ----------------------------------------------------

@app.route('/')
def index():
    # Inicia um novo histórico de chat se não existir
    if 'historico' not in session:
        session['historico'] = assistente.iniciar_novo_chat()
    
    saudacao_html = assistente.enviar_saudacao()
    # O filtro | safe está correto para renderizar o HTML da IA
    return render_template('chat_interface.html', saudacao=saudacao_html)


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    pergunta = data.get('pergunta')
    historico_serializado = session.get('historico', [])
    
    if not pergunta:
        return jsonify({'erro': 'Pergunta vazia.'}), 400

    # Adiciona a pergunta do usuário ao histórico ANTES de enviar
    historico_serializado.append({
        "role": "user",
        "parts": [{"text": pergunta}]
    })

    # Obtém a resposta e o histórico atualizado (incluindo a resposta da IA)
    resposta_ia, novo_historico_gemini = assistente.obter_resposta_com_memoria(
        historico_serializado, 
        pergunta
    )
    
    # Atualiza o histórico na sessão (serializando novamente)
    novo_historico_serializado = [
        json.loads(item.model_dump_json()) 
        for item in novo_historico_gemini
    ]
    session['historico'] = novo_historico_serializado
    
    return jsonify({'resposta': resposta_ia})


@app.route('/admin/conhecimento', methods=['GET', 'POST'])
def admin_conhecimento():
    """Painel de administração para editar o arquivo de conhecimento."""
    mensagem = ""
    
    if request.method == 'POST':
        novo_conteudo = request.form['novo_conhecimento']
        
        if salvar_novo_conhecimento(novo_conteudo):
            # Recarrega a instância do assistente para forçar a leitura do novo arquivo
            assistente.conhecimento_texto = ler_conhecimento_atual()
            mensagem = "Conhecimento atualizado com sucesso! (A IA recarregou o novo texto.)"
        else:
            mensagem = "Erro ao salvar o novo conhecimento. Verifique as permissões."
            
        conteudo_atual = novo_conteudo
    else:
        conteudo_atual = ler_conhecimento_atual()

    return render_template('admin_conhecimento.html', 
                           conteudo_atual=conteudo_atual, 
                           mensagem=mensagem)


if __name__ == '__main__':
    # Rodar em ambiente local
    app.run(debug=True)