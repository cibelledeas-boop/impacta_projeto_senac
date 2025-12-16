document.addEventListener('DOMContentLoaded', function() {
    
    // Elementos principais do layout
    const dmContainer = document.querySelector('.dm-container');
    const dmLista = document.querySelector('.dm-lista ul');
    const dmChat = document.querySelector('.dm-chat');

    // --- 1. Funcionalidade do Sidebar (Marcação Ativa) ---
    
    const path = window.location.pathname;
    const sidebarLinks = document.querySelectorAll('.sidebar nav a');

    sidebarLinks.forEach(link => {
        // Verifica se o caminho do link corresponde ao caminho atual
        if (link.getAttribute('href') === path) {
            link.classList.add('active');
        } else if (path === '/' && link.getAttribute('href') === '/landing') {
             // Caso especial: se estiver na raiz, assume que é a landing page
            link.classList.add('active');
        }
    });

    // --- 2. Funcionalidade da Lista de Conversas (DM) e Redirecionamento de Perfil ---
    
    // Função para simular o carregamento de uma conversa
    function carregarConversa(nome, ativa) {
        
        // Atualiza o header do chat
        const chatHeader = dmChat.querySelector('.chat-header h3');
        if (chatHeader) {
             chatHeader.textContent = nome;
        }

        // Não insere mensagens fake
        const chatMensagens = dmChat.querySelector('.chat-mensagens');
        if (chatMensagens) {
            chatMensagens.innerHTML = '';
            chatMensagens.scrollTop = chatMensagens.scrollHeight;
        }
        
        // Exibe a área do chat
        dmChat.style.display = 'flex'; 
    }

    // Adiciona o listener principal para todos os cliques na lista de conversas
    if (dmLista) {
        dmLista.addEventListener('click', function(event) {
            
            // 2.1. LÓGICA DE REDIRECIONAMENTO DE PERFIL (PRIORIDADE)
            // Verifica se o clique foi no elemento <strong> (o nome do usuário)
            const nomeElemento = event.target.closest('.info strong');
            
            if (nomeElemento) {
                event.preventDefault(); // Impede o comportamento padrão, se houver
                event.stopPropagation(); // Impede o clique de ativar a seleção da conversa
                
                const username = nomeElemento.textContent.replace('@', ''); // Pega o nome sem o '@'
                
                // Redireciona o usuário para a página de perfil (Exemplo: /perfil/amigolegal)
                window.location.href = `/perfil/${username}`;
                
                return; // Encerra a execução para não carregar a conversa
            }
            
            // 2.2. LÓGICA DE SELEÇÃO DE CONVERSA (Se não clicou no nome)
            
            const listItem = event.target.closest('li');
            if (!listItem) return;

            // Remove 'ativo' de todos os itens
            dmLista.querySelectorAll('li').forEach(item => {
                item.classList.remove('ativo');
            });

            // Adiciona 'ativo' ao item clicado
            listItem.classList.add('ativo');

            // Carrega a conversa simulada
            const nomeUsuario = listItem.querySelector('.info strong').textContent;
            const isAtivo = listItem.classList.contains('ativo');
            carregarConversa(nomeUsuario, isAtivo);
        });

        // 2.3. Carrega a primeira conversa ao carregar a página
        const primeiraConversa = dmLista.querySelector('li.ativo');
        if (primeiraConversa) {
            const nomeUsuario = primeiraConversa.querySelector('.info strong').textContent;
            carregarConversa(nomeUsuario, true);
        } else {
             // Se nenhuma estiver ativa, ativa a primeira por padrão
             const primeiroItem = dmLista.querySelector('li');
             if(primeiroItem) {
                 primeiroItem.classList.add('ativo');
                 const nome = primeiroItem.querySelector('.info strong').textContent;
                 carregarConversa(nome, true);
             }
        }
    }


    // --- 3. Funcionalidade de Envio de Mensagem (Simulado) ---

    const inputForm = dmChat.querySelector('.chat-input');
    const inputField = dmChat.querySelector('.chat-input input');
    const chatMensagens = dmChat.querySelector('.chat-mensagens');

    function enviarMensagem(e) {
        if (e && e.preventDefault) {
             e.preventDefault(); // Impede o recarregamento da página (se for evento de submit)
        }
       
        const texto = inputField.value.trim();

        if (texto !== "") {
            // Cria e insere a nova mensagem enviada
            const novaMsg = document.createElement('div');
            novaMsg.className = 'msg enviada';
            novaMsg.textContent = texto;
            chatMensagens.appendChild(novaMsg);

            // Limpa o input e foca
            inputField.value = '';
            inputField.focus();

            // Rola para a última mensagem
            chatMensagens.scrollTop = chatMensagens.scrollHeight;

            // Simula uma resposta após um pequeno delay
            setTimeout(() => {
                const resposta = document.createElement('div');
                resposta.className = 'msg recebida';
                resposta.textContent = 'Mensagem recebida com sucesso! Obrigado.';
                chatMensagens.appendChild(resposta);
                chatMensagens.scrollTop = chatMensagens.scrollHeight;
            }, 1000);
        }
    }

    if (inputForm) {
        // Listener para o evento 'submit' do formulário (acontece ao apertar Enter ou clicar no botão)
        inputForm.addEventListener('submit', enviarMensagem);
    }
    
});