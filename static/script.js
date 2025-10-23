// script.js - VERSÃO V60.0 (Microfone e Lógica de Chat)

document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('pergunta-input');
    const enviarBtn = document.getElementById('enviar-btn');
    const microphoneBtn = document.getElementById('microphone-btn');
    const chatBox = document.getElementById('chat-box');

    // --- Lógica de Habilitar/Desabilitar Botão Enviar ---
    function updateSendButton() {
        if (input.value.trim().length > 0) {
            enviarBtn.style.display = 'flex'; // Mostra avião
            microphoneBtn.style.display = 'none'; // Esconde microfone
            enviarBtn.disabled = false;
        } else {
            enviarBtn.style.display = 'none'; // Esconde avião
            microphoneBtn.style.display = 'flex'; // Mostra microfone
            enviarBtn.disabled = true;
        }
    }

    input.addEventListener('input', updateSendButton);
    input.addEventListener('keydown', function(e) {
        // Enviar com Shift + Enter ou apenas Enter se não for em dispositivos móveis
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (input.value.trim().length > 0) {
                enviarBtn.click();
            }
        }
        // Ajusta a altura da textarea dinamicamente
        input.style.height = 'auto';
        input.style.height = input.scrollHeight + 'px';
    });

    // --- Criação de Bolhas de Mensagem ---
    function criarBolha(texto, tipo) {
        const div = document.createElement('div');
        div.classList.add('mensagem', tipo);
        div.innerHTML = texto;
        chatBox.appendChild(div);
        
        // CRÍTICO: Auto-scroll para a última mensagem
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // --- Lógica Principal de Envio ---
    function enviarMensagem() {
        const pergunta = input.value.trim();
        if (!pergunta) return;

        // 1. Adiciona a mensagem do usuário
        criarBolha(pergunta, 'usuario');
        
        // 2. Limpa o input e atualiza botões
        input.value = '';
        input.style.height = 'auto'; // Reseta a altura da textarea
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
        .then(response => response.json())
        .then(data => {
            // 5. Substitui o placeholder pela resposta real
            iaPlaceholder.innerHTML = data.resposta;
        })
        .catch(error => {
            console.error('Erro ao comunicar com a API:', error);
            iaPlaceholder.innerHTML = 'Desculpe, houve um erro de conexão com o servidor.';
        });
    }

    enviarBtn.addEventListener('click', enviarMensagem);
    
    // --- Lógica do Microfone (Web Speech API) ---
    // Verifica se o navegador suporta a API de Reconhecimento de Fala
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition;
    let isListening = false;
    
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.lang = 'pt-BR'; // Define o idioma
        recognition.interimResults = false; // Retorna apenas o resultado final
        recognition.maxAlternatives = 1;

        recognition.onstart = function() {
            isListening = true;
            microphoneBtn.querySelector('i').classList.remove('fa-microphone');
            microphoneBtn.querySelector('i').classList.add('fa-microphone-alt', 'fa-beat-fade'); // Efeito de escuta
            microphoneBtn.style.color = '#FF4500'; // Cor de gravação (Laranja/Vermelho)
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
            microphoneBtn.style.color = ''; // Retorna à cor CSS normal
            input.placeholder = "Peça à Hope...";
        };

        recognition.onerror = function(event) {
            console.error('Erro no reconhecimento de fala:', event.error);
            // Mensagem de erro sutil
            input.placeholder = "Erro no Microfone. Tente digitar.";
            // Força o final
            recognition.stop(); 
        };

        microphoneBtn.addEventListener('click', function() {
            if (isListening) {
                recognition.stop();
            } else {
                // Remove qualquer texto anterior e começa a escutar
                input.value = ''; 
                updateSendButton();
                recognition.start();
            }
        });
        
    } else {
        // Se o navegador não suportar, esconde o botão MIC
        microphoneBtn.style.display = 'none';
        enviarBtn.style.display = 'flex';
        enviarBtn.disabled = true; // Por segurança, força o usuário a digitar
        console.warn('Reconhecimento de fala não suportado neste navegador.');
    }

    // Garante que os botões iniciais estejam corretos ao carregar
    updateSendButton();
});