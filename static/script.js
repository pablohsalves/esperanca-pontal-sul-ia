// static/script.js - Versão FINAL CORRIGIDA

document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('pergunta-input'); 
    const enviarBtn = document.getElementById('enviar-btn');
    const microphoneBtn = document.getElementById('microphone-btn');
    const chatBox = document.getElementById('chat-box');
    
    let singleRowHeight = 0; 
    let recognition = null; 

    // Inicializa a rolagem
    rolarParaBaixo(); 

    function rolarParaBaixo() {
        chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: 'smooth' });
    }
    
    function autoExpand() {
        if (singleRowHeight === 0) {
            input.style.height = 'auto';
            // Calcula a altura da primeira linha ao carregar
            singleRowHeight = input.scrollHeight;
        }
        
        input.style.height = 'auto'; 
        input.style.height = input.scrollHeight + 'px';
        
        rolarParaBaixo();
    }
    
    input.addEventListener('input', autoExpand);
    autoExpand(); 

    function adicionarMensagem(texto, remetente) {
        const div = document.createElement('div');
        div.className = `mensagem ${remetente}`;
        const htmlContent = texto.replace(/\n/g, '<br>');
        div.innerHTML = htmlContent;
        chatBox.appendChild(div);
        rolarParaBaixo();
        return div;
    }

    async function enviarMensagem() {
        const pergunta = input.value.trim();
        
        // Garante que o input não esteja vazio
        if (pergunta === '') { return; }

        adicionarMensagem(pergunta, 'usuario');
        
        // Reseta o input para o estado inicial (1 linha)
        input.value = ''; 
        input.style.height = singleRowHeight + 'px';
        
        input.disabled = true;
        enviarBtn.disabled = true;

        const loadingDiv = adicionarMensagem('Digitando...', 'ia');

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pergunta: pergunta })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ erro: 'Erro de comunicação desconhecido.' }));
                throw new Error(errorData.erro || `Erro HTTP: ${response.status}`);
            }

            const data = await response.json();
            chatBox.removeChild(loadingDiv);
            adicionarMensagem(data.resposta, 'ia');

        } catch (error) {
            chatBox.removeChild(loadingDiv);
            console.error('Erro ao enviar mensagem:', error);
            let erroDisplay = error.message;
            if (erroDisplay.includes('Erro HTTP: 500')) {
                erroDisplay = "Erro do Servidor Interno. Tente recarregar a página.";
            } else if (erroDisplay.includes('Failed to fetch')) {
                erroDisplay = "Erro de conexão: Não foi possível alcançar o servidor.";
            }
            adicionarMensagem(`Erro: ${erroDisplay}`, 'ia');
            
        } finally {
            input.disabled = false;
            enviarBtn.disabled = false;
            input.focus();
            rolarParaBaixo();
        }
    }
    
    // --- Lógica de Reconhecimento de Fala (Web Speech API) ---

    function varToCSS(varName) {
        return getComputedStyle(document.documentElement).getPropertyValue(varName).trim();
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const isSupported = !!SpeechRecognition;

    if (isSupported) {
        recognition = new SpeechRecognition();
        recognition.continuous = false; 
        recognition.lang = 'pt-BR';
        
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            input.value = transcript;
            autoExpand(); 
            // AÇÃO CRÍTICA: Envia a mensagem automaticamente após capturar
            enviarMensagem(); 
        };

        recognition.onstart = () => {
            microphoneBtn.style.color = 'red'; 
            microphoneBtn.innerHTML = '<i class="fas fa-dot-circle"></i>'; // Ponto de escuta
            input.placeholder = 'Escutando... Fale agora.';
        };
        
        recognition.onend = () => {
            microphoneBtn.style.color = varToCSS('--color-highlight'); 
            microphoneBtn.innerHTML = '<i class="fas fa-microphone"></i>'; // Microfone
            input.placeholder = 'Peça à Esperança';
        };
        
        recognition.onerror = (event) => {
            console.error('Erro de reconhecimento de fala:', event.error);
            microphoneBtn.style.color = varToCSS('--color-highlight');
            microphoneBtn.innerHTML = '<i class="fas fa-microphone"></i>';
            input.placeholder = 'Peça à Esperança';
            
            if (event.error === 'not-allowed') {
                 alert("Acesso ao microfone negado. Verifique as permissões do seu navegador.");
            }
        };

        microphoneBtn.addEventListener('click', () => {
            try {
                if (input.disabled) return; 
                
                if (recognition.recognizing) {
                    recognition.stop();
                } else {
                    input.value = '';
                    autoExpand();
                    recognition.start();
                }
            } catch (e) {
                 console.error("Não foi possível iniciar o reconhecimento de fala.", e);
            }
        });

    } else {
        // Se não suportar voz, esconde o microfone e ajusta o padding do input
        microphoneBtn.style.display = 'none';
        input.style.paddingLeft = '20px'; 
    }


    // --- Ativar o envio por Enter e Clique ---
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) { 
            e.preventDefault(); 
            enviarMensagem();
        }
    });

    enviarBtn.addEventListener('click', enviarMensagem);
});