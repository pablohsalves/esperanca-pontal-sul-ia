// script.js - VERSÃO V60.0-FINAL (Tratamento de Erro de "Digitando..." Corrigido)

document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('pergunta-input');
    const enviarBtn = document.getElementById('enviar-btn');
    const microphoneBtn = document.getElementById('microphone-btn');
    const chatBox = document.getElementById('chat-box');

    // --- Lógica de Habilitar/Desabilitar Botão Enviar ---
    function updateSendButton() {
        // ... (código mantido) ...
        if (input.value.trim().length > 0) {
            enviarBtn.style.display = 'flex'; 
            microphoneBtn.style.display = 'none'; 
            enviarBtn.disabled = false;
        } else {
            enviarBtn.style.display = 'none'; 
            microphoneBtn.style.display = 'flex'; 
            enviarBtn.disabled = true;
        }
    }

    input.addEventListener('input', updateSendButton);
    input.addEventListener('keydown', function(e) {
        // ... (código mantido) ...
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (input.value.trim().length > 0) {
                enviarBtn.click();
            }
        }
        input.style.height = 'auto';
        input.style.height = input.scrollHeight + 'px';
    });

    // --- Criação de Bolhas de Mensagem ---
    function criarBolha(texto, tipo) {
        const div = document.createElement('div');
        div.classList.add('mensagem', tipo);
        // CRÍTICO: Usar innerText ou textContent se o texto for puro.
        // Se a IA retornar formatação, usamos innerHTML (como está no seu código)
        div.innerHTML = texto; 
        chatBox.appendChild(div);
        
        chatBox.scrollTop = chatBox.scrollHeight;
        return div; // Retorna a div para que possa ser atualizada
    }

    // --- Lógica Principal de Envio ---
    function enviarMensagem() {
        const pergunta = input.value.trim();
        if (!pergunta) return;

        // 1. Adiciona a mensagem do usuário
        criarBolha(pergunta, 'usuario');
        
        // 2. Limpa o input e atualiza botões
        input.value = '';
        input.style.height = 'auto'; 
        updateSendButton();
        
        // 3. Adiciona um placeholder de resposta da IA
        const iaPlaceholder = criarBolha('<i class="fas fa-spinner fa-spin"></i> Digitanto...', 'ia');

        // 4. Envia para a API Flask
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ pergunta: pergunta })
        })
        .then(response => {
            // CRÍTICO: Verifica o status HTTP da resposta do Flask
            if (!response.ok) {
                // Se o Flask retornar um erro HTTP (4xx ou 5xx), tratamos aqui
                throw new Error(`Erro de rede do servidor: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // 5. Substitui o placeholder pela resposta real
            // Se o Flask retornar o JSON com a chave 'resposta', exibe
            if (data && data.resposta) {
                 iaPlaceholder.innerHTML = data.resposta;
            } else {
                // Caso o JSON esteja vazio ou mal-formado (improvável com as últimas correções)
                iaPlaceholder.innerHTML = 'Desculpe, a IA retornou um formato de resposta inesperado.';
            }
           
        })
        .catch(error => {
            // 6. TRATAMENTO DE ERRO CRÍTICO (Resolve o problema do "Digitando...")
            console.error('Erro ao comunicar com a API ou servidor:', error);
            
            // Mensagem de erro amigável, indicando sobrecarga ou falha de conexão
            iaPlaceholder.innerHTML = 'Desculpe, ocorreu um erro temporário (API sobrecarregada ou falha de rede). Por favor, tente novamente em alguns segundos.';
        });
    }

    enviarBtn.addEventListener('click', enviarMensagem);
    
    // --- Lógica do Microfone (Web Speech API) ---
    // ... (código do microfone mantido) ...
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition;
    let isListening = false;
    
    if (SpeechRecognition) {
        // ... (código de inicialização e eventos do microfone mantido) ...
        recognition = new SpeechRecognition();
        recognition.lang = 'pt-BR'; 
        recognition.interimResults = false; 
        recognition.maxAlternatives = 1;

        recognition.onstart = function() {
            isListening = true;
            microphoneBtn.querySelector('i').classList.remove('fa-microphone');
            microphoneBtn.querySelector('i').classList.add('fa-microphone-alt', 'fa-beat-fade'); 
            microphoneBtn.style.color = '#FF4500'; 
            input.placeholder = "Escutando... Fale agora.";
        };

        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            input.value = transcript;
            updateSendButton();
            // Envia a mensagem automaticamente após o resultado
            enviarMensagem(); 
        };

        recognition.onend = function() {
            isListening = false;
            microphoneBtn.querySelector('i').classList.remove('fa-microphone-alt', 'fa-beat-fade');
            microphoneBtn.querySelector('i').classList.add('fa-microphone');
            microphoneBtn.style.color = ''; 
            input.placeholder = "Peça à Hope...";
        };

        recognition.onerror = function(event) {
            console.error('Erro no reconhecimento de fala:', event.error);
            input.placeholder = "Erro no Microfone. Tente digitar.";
            recognition.stop(); 
        };

        microphoneBtn.addEventListener('click', function() {
            if (isListening) {
                recognition.stop();
            } else {
                input.value = ''; 
                updateSendButton();
                recognition.start();
            }
        });
        
    } else {
        microphoneBtn.style.display = 'none';
        enviarBtn.style.display = 'flex';
        enviarBtn.disabled = true; 
        console.warn('Reconhecimento de fala não suportado neste navegador.');
    }

    updateSendButton();
});