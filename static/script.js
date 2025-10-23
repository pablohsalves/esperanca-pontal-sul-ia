// static/script.js - VERSÃO V60.50 (Saudação Restaurada)

// --- Funções de Ajuda ---

// Função de conversão que suporta **negrito** (Markdown) e *negrito* (WhatsApp/Telegram)
function simpleMarkdownToHtml(text) {
    // 1. Converte **negrito** para <strong>negrito</strong> (Markdown Padrão)
    let html = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // 2. Converte *negrito* para <strong>negrito</strong> (Sintaxe WhatsApp/Telegram)
    html = html.replace(/\*(.*?)\*/g, '<strong>$1</strong>');
    
    // 3. Converte \n em <br> para quebras de linha
    html = html.replace(/\n/g, '<br>');
    
    return html;
}

function createMessageElement(text, sender, type = 'text', data = null) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('mensagem', sender);
    
    if (type === 'button' && data) {
        // Renderiza mensagem de pré-texto (opcional) e botão de ação
        const preText = document.createElement('p');
        preText.innerHTML = simpleMarkdownToHtml(data.pre_text);
        messageElement.appendChild(preText);

        const actionContainer = document.createElement('div');
        actionContainer.classList.add('ia-action-button');

        const buttonLink = document.createElement('a');
        buttonLink.href = data.button_url;
        buttonLink.target = '_blank';
        buttonLink.classList.add('button-link');
        
        const icon = document.createElement('i');
        icon.className = data.button_icon;
        
        buttonLink.appendChild(icon);
        buttonLink.appendChild(document.createTextNode(data.button_text));
        
        actionContainer.appendChild(buttonLink);
        messageElement.appendChild(actionContainer);
        
    } else {
        // Renderiza mensagem de texto padrão, convertendo Markdown
        messageElement.innerHTML = simpleMarkdownToHtml(text);
    }

    return messageElement;
}

function appendMessage(text, sender, type = 'text', data = null) {
    const chatBox = document.getElementById('chat-box');
    const messageElement = createMessageElement(text, sender, type, data);
    
    // Remove o indicador de digitação se existir antes de adicionar a resposta
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        chatBox.removeChild(typingIndicator);
    }

    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function showTypingIndicator() {
    const chatBox = document.getElementById('chat-box');
    let typingIndicator = document.getElementById('typing-indicator');

    if (!typingIndicator) {
        typingIndicator = document.createElement('div');
        typingIndicator.id = 'typing-indicator';
        typingIndicator.classList.add('mensagem', 'ia');
        typingIndicator.innerHTML = '<i class="fas fa-ellipsis-h"></i>';
        chatBox.appendChild(typingIndicator);
    }
    chatBox.scrollTop = chatBox.scrollHeight;
}


// --- Lógica Principal ---

document.addEventListener('DOMContentLoaded', function() {
    const chatBox = document.getElementById('chat-box');
    const form = document.getElementById('chat-form');
    const input = document.getElementById('pergunta-input');
    
    // 1. Renderizar Saudação Inicial
    // V60.50: Usa a variável global (definida no HTML) para garantir a renderização
    if (typeof INITIAL_SAUDACAO_TEXT !== 'undefined' && INITIAL_SAUDACAO_TEXT.trim() !== '') {
        appendMessage(INITIAL_SAUDACAO_TEXT, 'ia');
    }

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        const userMessage = input.value.trim();
        
        if (userMessage === "") return;

        // 1. Exibir mensagem do usuário
        appendMessage(userMessage, 'usuario');
        input.value = ''; // Limpa o input
        
        // 2. Exibir indicador de digitação
        showTypingIndicator();

        // 3. Enviar mensagem para a API
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ mensagem: userMessage })
            });

            const data = await response.json();
            
            // 4. Exibir resposta da IA
            if (data.type === 'button') {
                appendMessage(null, 'ia', 'button', data);
            } else {
                appendMessage(data.resposta, 'ia');
            }
            
        } catch (error) {
            console.error('Erro ao comunicar com a API:', error);
            appendMessage("Desculpe, houve um erro ao processar sua solicitação. Tente novamente.", 'ia');
        }
    });
    
    // Ajuste: Permite o envio da mensagem ao pressionar ENTER no campo de texto
    input.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault(); // Impede a quebra de linha
            form.dispatchEvent(new Event('submit')); // Dispara o evento de submit
        }
    });
});