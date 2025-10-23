// static/script.js - VERSÃO V60.53 (Microfone Restaurado)

// ... (Funções createMessageElement e simpleMarkdownToHtml, appendMessage, showTypingIndicator) ...

document.addEventListener('DOMContentLoaded', function() {
    const chatBox = document.getElementById('chat-box');
    const form = document.getElementById('chat-form');
    const input = document.getElementById('pergunta-input');
    // Adiciona a referência ao botão do microfone
    const microphoneBtn = document.getElementById('microphone-btn'); 
    
    // 1. Renderizar Saudação Inicial
    if (typeof INITIAL_SAUDACAO_TEXT !== 'undefined' && INITIAL_SAUDACAO_TEXT.trim() !== '') {
        appendMessage(INITIAL_SAUDACAO_TEXT, 'ia');
    }

    // 2. LÓGICA DE RECONHECIMENTO DE VOZ (V60.53: RESTAURADA)
    // Verifica o suporte do navegador (Chrome usa webkitSpeechRecognition)
    if ('webkitSpeechRecognition' in window) {
        
        microphoneBtn.disabled = false; // Habilita o botão
        
        const recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'pt-BR'; // Define o idioma para Português do Brasil

        let isListening = false;
        
        microphoneBtn.addEventListener('click', () => {
            if (isListening) {
                recognition.stop();
            } else {
                recognition.start();
                // Altera o visual do botão para indicar que está escutando
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
            form.dispatchEvent(new Event('submit')); // Envia a mensagem após o resultado
        };

        recognition.onend = () => {
            isListening = false;
            // Restaura o visual do botão
            microphoneBtn.style.color = 'var(--color-text-secondary)'; 
            microphoneBtn.style.backgroundColor = 'transparent';
            input.placeholder = "Peça à Hope..."; // Restaura o placeholder
        };

        recognition.onerror = (event) => {
            console.error('Erro no reconhecimento de fala:', event.error);
            isListening = false;
            // Restaura o visual do botão em caso de erro
            microphoneBtn.style.color = 'var(--color-text-secondary)'; 
            microphoneBtn.style.backgroundColor = 'transparent';
            input.placeholder = "Peça à Hope..."; // Restaura o placeholder
        };
        
    } else {
        // Remove o botão de navegadores não suportados
        microphoneBtn.style.display = 'none';
        
        // Se o botão for removido, o botão de envio deve ser reajustado
        // Não é necessário, pois o botão de envio usa 'right: 10px', que é relativo ao seu pai
    }
    
    // 3. Lógica de envio do formulário (mantida)
    form.addEventListener('submit', async function(e) {
        // ... (seu código de envio) ...
    });
    
    // Ajuste: Permite o envio da mensagem ao pressionar ENTER no campo de texto (mantido)
    input.addEventListener('keydown', function(event) {
        // ... (seu código de keydown) ...
    });
});