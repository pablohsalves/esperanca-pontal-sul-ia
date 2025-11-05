// static/script.js - VERSÃO V60.55 (Envio de Áudio Restaurado)

// --- Funções de Ajuda ---

// Função de conversão que suporta **negrito** (Markdown) e *negrito* (WhatsApp/Telegram)
function simpleMarkdownToHtml(text) {
    let html = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.*?)\*/g, '<strong>$1</strong>');
    html = html.replace(/\n/g, '<br>');
    return html;
}

function createMessageElement(text, sender, type = 'text', data = null) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('mensagem', sender);
    
    if (type === 'button' && data) {
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
        messageElement.innerHTML = simpleMarkdownToHtml(text);
    }

    return messageElement;
}

function appendMessage(text, sender, type = 'text', data = null) {
    const chatBox = document.getElementById('chat-box');
    const messageElement = createMessageElement(text, sender, type, data);
    
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
    const microphoneBtn = document.getElementById('microphone-btn'); 
    
    // 1. Renderizar Saudação Inicial
    if (typeof INITIAL_SAUDACAO_TEXT !== 'undefined' && INITIAL_SAUDACAO_TEXT.trim() !== '') {
        appendMessage(INITIAL_SAUDACAO_TEXT, 'ia');
    }

    // 2. LÓGICA DE RECONHECIMENTO DE VOZ
    if ('webkitSpeechRecognition' in window) {
        
        microphoneBtn.disabled = false; // Habilita o botão
        
        const recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'pt-BR'; // Define o idioma

        let isListening = false;
        
        microphoneBtn.addEventListener('click', () => {
            if (isListening) {
                recognition.stop();
            } else {
                input.value = ''; 
                recognition.start();
                // Altera o visual
                microphoneBtn.style.color = 'red'; 
                microphoneBtn.style.backgroundColor = 'rgba(255, 0, 0, 0.2)';
            }
        });

        recognition.onstart = () => {
            isListening = true;
            input.placeholder = "Escutando...";
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            input.value = transcript;
            
            // AJUSTE V60.55: Dispara o envio do formulário
            form.dispatchEvent(new Event('submit')); 
        };

        recognition.onend = () => {
            isListening = false;
            // Restaura o visual
            microphoneBtn.style.color = 'var(--color-text-secondary)'; 
            microphoneBtn.style.backgroundColor = 'transparent';
            input.placeholder = "Peça à Hope..."; 
        };

        recognition.onerror = (event) => {
            console.error('Erro no reconhecimento de fala:', event.error);
            isListening = false;
            // Restaura o visual em caso de erro
            microphoneBtn.style.color = 'var(--color-text-secondary)'; 
            microphoneBtn.style.backgroundColor = 'transparent';
            input.placeholder = "Peça à Hope..."; 
        };
        
    } else {
        // Remove o botão de navegadores não suportados
        microphoneBtn.style.display = 'none';
    }
    
    // 3. Lógica de envio do formulário
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

            if (!response.ok) {
                throw new Error(`Erro de rede: ${response.status}`);
            }

            const data = await response.json();
            
            // 4. Exibir resposta da IA
            if (data.type === 'button') {
                appendMessage(null, 'ia', 'button', data);
            } else {
                appendMessage(data.resposta, 'ia');
            }
            
        } catch (error) {
            console.error('Erro ao comunicar com a API:', error);
            // Mensagem de erro para o usuário (mostrada na bolha da IA)
            appendMessage("Desculpe, ocorreu um erro de conexão. Por favor, tente novamente.", 'ia'); 
            
            // Remove o indicador de digitação em caso de erro
            const typingIndicator = document.getElementById('typing-indicator');
            if (typingIndicator) {
                typingIndicator.remove();
            }
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