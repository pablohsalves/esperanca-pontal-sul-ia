// static/script.js - Versão FINAL com Chips Dinâmicos, Microfone e Correção de Rolagem

document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('pergunta-input'); 
    const enviarBtn = document.getElementById('enviar-btn');
    const microphoneBtn = document.getElementById('microphone-btn');
    const chatBox = document.getElementById('chat-box');
    
    let singleRowHeight = 0; 
    let recognition = null; 

    // O ROLAMENTO É FEITO NO BODY/HTML
    function rolarParaBaixo() {
        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    }
    
    function autoExpand() {
        if (singleRowHeight === 0) {
            input.style.height = 'auto';
            singleRowHeight = input.scrollHeight;
        }
        
        input.style.height = 'auto'; 
        input.style.height = input.scrollHeight + 'px';
        
        rolarParaBaixo();
    }
    
    input.addEventListener('input', autoExpand);
    autoExpand(); 
    rolarParaBaixo(); 

    function adicionarMensagem(texto, remetente) {
        const div = document.createElement('div');
        div.className = `mensagem ${remetente}`;
        // CRÍTICO: A resposta da IA já contém tags HTML de chips e <br>
        div.innerHTML = texto; 
        chatBox.appendChild(div);
        rolarParaBaixo();
        return div;
    }

    async function enviarMensagem() {
        const pergunta = input.value.trim();
        
        if (pergunta === '') { return; }

        // Remove os chips de sugestão do topo após a primeira interação
        const suggestionChipsContainer = document.querySelector('.suggestion-chips');
        if (suggestionChipsContainer) {
            // Garante que a primeira interação remova os botões de boas-vindas
            suggestionChipsContainer.style.display = 'none'; 
        }

        // 1. Exibe a mensagem do usuário
        adicionarMensagem(pergunta, 'usuario'); 
        
        // 2. Reseta o input e desabilita
        input.value = ''; 
        input.style.height = singleRowHeight + 'px';
        
        input.disabled = true;
        enviarBtn.disabled = true;
        microphoneBtn.disabled = true;

        // 3. Adiciona o indicador de carregamento
        const loadingDiv = adicionarMensagem('<span class="loading-indicator"></span>Esperança está processando...', 'ia');

        try {
            // 4. Envia a requisição
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
            
            // 5. Remove o indicador de carregamento
            if(loadingDiv.parentNode) {
                chatBox.removeChild(loadingDiv);
            }
            
            // 6. Exibe a resposta final da IA
            // O texto retornado da IA já contém a formatação HTML com os chips
            adicionarMensagem(data.resposta, 'ia'); 

        } catch (error) {
            if(loadingDiv.parentNode) {
                chatBox.removeChild(loadingDiv);
            }
            console.error('Erro ao enviar mensagem:', error);
            let erroDisplay = error.message;
            if (erroDisplay.includes('Erro HTTP')) {
                erroDisplay = "Erro do Servidor. Tente recarregar a página ou verifique o log de IA.";
            } else if (erroDisplay.includes('Failed to fetch')) {
                erroDisplay = "Erro de conexão: Não foi possível alcançar o servidor.";
            }
            // Usa o texto de erro dentro da tag <p>
            adicionarMensagem(`<p>Erro: ${erroDisplay}</p>`, 'ia'); 
            
        } finally {
            // 7. Reabilita e foca
            input.disabled = false;
            enviarBtn.disabled = false;
            microphoneBtn.disabled = false;
            input.focus();
            rolarParaBaixo();
        }
    }
    
    // --- LÓGICA DE RECONHECIMENTO DE FALA (MICROFONE) ---

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.lang = 'pt-BR'; 
        recognition.interimResults = false; 
        recognition.maxAlternatives = 1;

        microphoneBtn.addEventListener('click', () => {
            if (microphoneBtn.classList.contains('recording')) {
                recognition.stop();
            } else {
                recognition.start();
            }
        });

        recognition.onstart = () => {
            microphoneBtn.classList.add('recording');
            microphoneBtn.style.color = '#ff5555'; 
            input.placeholder = 'Escutando... Fale agora.';
            input.disabled = true;
            enviarBtn.disabled = true;
        };

        recognition.onresult = (event) => {
            const speechResult = event.results[0][0].transcript;
            input.value = speechResult;
            enviarMensagem(); 
        };

        recognition.onend = () => {
            microphoneBtn.classList.remove('recording');
            microphoneBtn.style.color = 'var(--color-highlight)'; 
            input.placeholder = 'Peça à Esperança';
            input.disabled = false;
            enviarBtn.disabled = false;
        };

        recognition.onerror = (event) => {
            console.error('Erro no reconhecimento de voz:', event.error);
            // Mensagem de erro visível para o usuário
            if (event.error === 'not-allowed') {
                 alert('Acesso ao microfone negado. Verifique as permissões do seu navegador.');
            } 
            recognition.onend(); 
        };

    } else {
        microphoneBtn.style.display = 'none';
    }
    
    // --- Lógica de Envio (Enter e Clique) ---
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) { 
            e.preventDefault(); 
            enviarMensagem();
        }
    });

    enviarBtn.addEventListener('click', enviarMensagem);
    
    // --- Lógica para Chips/Botões Clicáveis (Abre URL ou Envia Pergunta) ---
    chatBox.addEventListener('click', (e) => {
        // Encontra o chip mais próximo do clique
        const chip = e.target.closest('.chip'); 
        if (chip) {
            const url = chip.getAttribute('data-url');
            const isSuggestion = chip.classList.contains('suggestion-chip');
            
            if (url) {
                if (!isSuggestion) {
                    // Chip de resposta da IA: Abre em nova aba
                    window.open(url, '_blank');
                } else {
                    // Chip de Sugestão (Botão de Boas-vindas)
                    const text = chip.getAttribute('data-text');
                    
                    if (url.startsWith('/')) {
                        // Navegação interna (ex: /#horarios)
                        window.location.href = url;
                    } else {
                        // Chips que devem enviar uma pergunta ao chat
                        let perguntaSugerida;
                        
                        // Lógica para criar uma pergunta a partir do texto do chip
                        if (text.includes("WhatsApp")) {
                             perguntaSugerida = "Qual é o número de WhatsApp da igreja?";
                        } else if (text.includes("Mapa")) {
                             perguntaSugerida = "Onde fica a igreja (endereço completo)?";
                        } else if (text.includes("Horários")) {
                             perguntaSugerida = "Quais são os horários dos cultos?";
                        } else {
                             perguntaSugerida = `Gostaria de saber mais sobre ${text.toLowerCase()}.`;
                        }

                        input.value = perguntaSugerida;
                        autoExpand();
                        enviarMensagem();
                    }
                }
            }
        }
    });
});