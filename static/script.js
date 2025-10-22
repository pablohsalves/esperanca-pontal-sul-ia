// static/script.js - Versão FINAL E ESTÁVEL com Rolagem, Chips e Microfone

document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('pergunta-input'); 
    const enviarBtn = document.getElementById('enviar-btn');
    const microphoneBtn = document.getElementById('microphone-btn');
    const chatBox = document.getElementById('chat-box');
    
    let singleRowHeight = 0; 
    let recognition = null; 

    // --- ROLAGEM E AUTOSIZE ---
    function rolarParaBaixo() {
        // Rola o corpo da página até o final (CSS controla o padding)
        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    }
    
    function autoExpand() {
        if (singleRowHeight === 0) {
            input.style.height = 'auto';
            // Garante que o singleRowHeight pegue a altura base do padding/font
            singleRowHeight = input.scrollHeight; 
            input.style.height = singleRowHeight + 'px';
        }
        
        input.style.height = 'auto'; 
        // Define a altura com base no conteúdo, respeitando o max-height
        input.style.height = input.scrollHeight + 'px'; 
        
        rolarParaBaixo();
    }
    
    input.addEventListener('input', autoExpand);
    // Garante que o autosize seja executado na inicialização
    setTimeout(autoExpand, 0); 
    rolarParaBaixo(); 


    // --- FUNÇÃO DE MENSAGEM ---
    function adicionarMensagem(texto, remetente) {
        const div = document.createElement('div');
        div.className = `mensagem ${remetente}`;
        // A resposta da IA já contém tags HTML de chips e quebras de linha (<br>)
        div.innerHTML = texto; 
        chatBox.appendChild(div);
        rolarParaBaixo();
        return div;
    }

    // --- FUNÇÃO PRINCIPAL DE ENVIO ---
    async function enviarMensagem() {
        const pergunta = input.value.trim();
        
        if (pergunta === '') { return; }

        // Remove os chips de sugestão do topo após a primeira interação
        const suggestionChipsContainer = document.querySelector('.suggestion-chips');
        if (suggestionChipsContainer) {
            suggestionChipsContainer.style.display = 'none'; 
        }

        // 1. Exibe a mensagem do usuário
        adicionarMensagem(pergunta, 'usuario'); 
        
        // 2. Reseta o input e desabilita
        input.value = ''; 
        input.style.height = singleRowHeight + 'px'; // Volta para 1 linha
        
        input.disabled = true;
        enviarBtn.disabled = true;
        microphoneBtn.disabled = true;

        rolarParaBaixo(); // Força a rolagem antes do indicador

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
                // Se estiver gravando, para a gravação
                recognition.stop();
            } else {
                // Se não estiver gravando, tenta iniciar
                try {
                    recognition.start();
                } catch (e) {
                    // Previne erro se tentar iniciar enquanto já está ativo
                    console.warn("Reconhecimento de voz já ativo ou falha ao iniciar.", e);
                }
            }
        });

        recognition.onstart = () => {
            microphoneBtn.classList.add('recording');
            microphoneBtn.style.color = '#ff5555'; // Vermelho
            input.placeholder = 'Escutando... Fale agora.';
            input.disabled = true;
            enviarBtn.disabled = true;
        };

        recognition.onresult = (event) => {
            const speechResult = event.results[0][0].transcript;
            input.value = speechResult;
            // Envia a mensagem imediatamente após o reconhecimento
            enviarMensagem(); 
        };

        recognition.onend = () => {
            microphoneBtn.classList.remove('recording');
            microphoneBtn.style.color = 'var(--color-highlight)'; // Volta à cor padrão
            input.placeholder = 'Peça à Esperança';
            input.disabled = false;
            enviarBtn.disabled = false;
        };

        recognition.onerror = (event) => {
            console.error('Erro no reconhecimento de voz:', event.error);
            // Chama onend para resetar o estado dos botões
            recognition.onend(); 
            // Informa ao usuário sobre a permissão
            if (event.error === 'not-allowed') {
                 alert('Acesso ao microfone negado. Verifique as permissões do seu navegador.');
            } 
        };

    } else {
        // Se a API não for suportada, esconde o botão
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
    
    // --- Lógica para Chips/Botões Clicáveis ---
    chatBox.addEventListener('click', (e) => {
        const chip = e.target.closest('.chip'); 
        if (chip) {
            const url = chip.getAttribute('data-url');
            const isSuggestion = chip.classList.contains('suggestion-chip');
            
            // Se o chip tiver um URL
            if (url) {
                
                // 1. CHIP DE RESPOSTA DA IA (Não é sugestão)
                if (!isSuggestion) {
                    e.preventDefault(); // Impede ação padrão do link se for link
                    window.open(url, '_blank');
                    return;
                } 
                
                // 2. CHIP DE SUGESTÃO (Botão de Boas-vindas)
                else {
                    const text = chip.getAttribute('data-text');
                    
                    if (url.startsWith('/')) {
                        // Navegação interna (ex: /#horarios)
                        window.location.href = url;
                    } else {
                        // Chips que devem enviar uma pergunta ao chat
                        let perguntaSugerida = text; // Usa o texto como sugestão inicial

                        // Se for um chip de contato, monta a pergunta correta
                        if (text.includes("WhatsApp")) {
                             perguntaSugerida = "Qual é o número de WhatsApp da igreja?";
                        } else if (text.includes("Mapa") || text.includes("Localização")) {
                             perguntaSugerida = "Onde fica a igreja (endereço completo)?";
                        } else if (text.includes("Horários")) {
                             perguntaSugerida = "Quais são os horários dos cultos?";
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