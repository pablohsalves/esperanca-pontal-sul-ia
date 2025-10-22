// static/script.js - Versão FINAL com Chips Dinâmicos e Correção de Rolagem

document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('pergunta-input'); 
    const enviarBtn = document.getElementById('enviar-btn');
    const microphoneBtn = document.getElementById('microphone-btn');
    const chatBox = document.getElementById('chat-box');
    
    let singleRowHeight = 0; 
    let recognition = null; 

    // O ROLAMENTO AGORA É FEITO NO BODY/HTML, NÃO NA CHAT-BOX
    function rolarParaBaixo() {
        // Rola o corpo da página até o final
        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    }
    
    function autoExpand() {
        if (singleRowHeight === 0) {
            input.style.height = 'auto';
            singleRowHeight = input.scrollHeight;
        }
        
        input.style.height = 'auto'; 
        input.style.height = input.scrollHeight + 'px';
        
        // Rolagem após expandir o input
        rolarParaBaixo();
    }
    
    input.addEventListener('input', autoExpand);
    // Chama para garantir o tamanho inicial correto
    autoExpand(); 
    rolarParaBaixo(); // Garante que a tela carregue no fim

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
        input.style.height = singleRowHeight + 'px';
        
        input.disabled = true;
        enviarBtn.disabled = true;

        // 3. Adiciona o indicador de carregamento (Pensando...)
        const loadingDiv = adicionarMensagem('<span class="loading-indicator"></span>Esperança está processando...', 'ia');

        try {
            // 4. Envia a requisição para o endpoint /api/chat
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
            adicionarMensagem(`Erro: ${erroDisplay}`, 'ia');
            
        } finally {
            // 7. Reabilita e foca
            input.disabled = false;
            enviarBtn.disabled = false;
            input.focus();
            rolarParaBaixo();
        }
    }
    
    // --- Lógica de Reconhecimento de Fala (Omitida por brevidade, mas mantida no arquivo) ---
    // ... (Código de Voz) ...

    // --- Ativar o envio por Enter e Clique (Campo de texto) ---
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) { 
            e.preventDefault(); 
            enviarMensagem();
        }
    });

    enviarBtn.addEventListener('click', enviarMensagem);
    
    // --- Lógica para Chips/Botões Clicáveis (Chat Box e Sugestões) ---
    chatBox.addEventListener('click', (e) => {
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
                    
                    // Se for um link de navegação interno, apenas navega (ex: Horários)
                    if (url.startsWith('/')) {
                        window.location.href = url;
                    } else {
                        // Para todos os outros, preenche o input e envia
                        let perguntaSugerida;
                        
                        if (text.includes("WhatsApp")) {
                             perguntaSugerida = "Qual é o número de WhatsApp da igreja?";
                        } else if (text.includes("Mapa")) {
                             perguntaSugerida = "Onde fica a igreja (endereço completo)?";
                        } else if (text.includes("Horários")) {
                             perguntaSugerida = "Quais são os horários dos cultos?";
                        } else {
                             // Fallback
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