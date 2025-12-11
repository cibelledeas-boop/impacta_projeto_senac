document.addEventListener('DOMContentLoaded', function() {
    
    // --- 1. Seleção de Elementos ---

    // === Modais e Botões de Ação ===
    // Modal de Edição de Perfil
    const editModal = document.getElementById('edit-modal');
    const openEditButton = document.getElementById('open-edit');
    const closeEditButton = document.getElementById('close-edit');
    const editForm = document.getElementById('edit-form');

    // Modal de Criação de Post
    const createPostModal = document.getElementById('create-post-modal');
    const openCreatePostButton = document.getElementById('open-post-modal'); // Botão da Sidebar
    const closeCreatePostButton = document.getElementById('close-create-post');
    const createPostForm = document.getElementById('create-post-form');

    // Modal de Visualização de Post
    const viewPostModal = document.getElementById('view-post-modal');
    const closeViewPostButton = document.getElementById('close-view-post');
    const postItems = document.querySelectorAll('.post-item'); // Itens na grade

    // === Elementos do Perfil e Formulários ===
    const nomePerfilDisplay = document.getElementById('nome-perfil');
    const bioPerfilDisplay = document.getElementById('bio-perfil');
    const perfilAvatarDisplay = document.querySelector('.perfil-avatar');
    
    // Edição
    const inputNome = document.getElementById('edit-nome');
    const inputBio = document.getElementById('edit-bio');
    const inputFile = document.getElementById('edit-file');
    const editAvatarPreview = document.querySelector('.edit-avatar');

    // Criação
    const createFileInput = document.getElementById('create-file-input');
    const createUploadBox = document.getElementById('upload-box-trigger');
    const createImagePreview = document.getElementById('create-image-preview');
    const createCaptionInput = document.getElementById('create-caption');

    
    // --- 2. Funções Auxiliares de Modal ---

    /** Abre um modal, bloqueando o scroll do body. */
    function openModal(modalElement) {
        modalElement.style.display = 'flex'; 
        document.body.style.overflow = 'hidden';
    }

    /** Fecha um modal, restaurando o scroll do body. */
    function closeModal(modalElement) {
        modalElement.style.display = 'none';
        document.body.style.overflow = 'auto';
    }

    // --- 3. Funcionalidade de Edição de Perfil ---
    
    // Abrir Modal de Edição
    if (openEditButton && editModal) {
        openEditButton.addEventListener('click', function() {
            // Carrega os dados atuais nos inputs do formulário
            inputNome.value = nomePerfilDisplay.textContent.trim();
            // Troca <br> por \n para textarea
            const currentBio = bioPerfilDisplay.innerHTML.replace(/<br>/g, '\n').trim();
            inputBio.value = currentBio; 
            editAvatarPreview.src = perfilAvatarDisplay.src; 
            openModal(editModal);
        });
    }

    // Fechar Modal de Edição
    if (closeEditButton) {
        closeEditButton.addEventListener('click', () => closeModal(editModal));
    }
    
    // Preview da imagem de Edição
    if (inputFile) {
        inputFile.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (event) => { editAvatarPreview.src = event.target.result; };
                reader.readAsDataURL(file);
            }
        });
    }

    // Submissão do Formulário de Edição (Salvar)
    if (editForm) {
        editForm.addEventListener('submit', function(e) {
            e.preventDefault(); 
            const novoNome = inputNome.value.trim();
            const novaBio = inputBio.value.trim();
            
            // Atualiza os elementos da página
            nomePerfilDisplay.textContent = novoNome;
            // Troca \n por <br> para display no HTML
            bioPerfilDisplay.innerHTML = novaBio.replace(/\n/g, '<br>');

            // Atualiza o avatar principal se houver alteração
            if (editAvatarPreview.src && editAvatarPreview.src !== perfilAvatarDisplay.src) {
                 perfilAvatarDisplay.src = editAvatarPreview.src; 
            }

            console.log('Dados do perfil salvos (Simulação):', { nome: novoNome, bio: novaBio });
            alert('Perfil atualizado com sucesso!');
            closeModal(editModal);
        });
    }
    
    // ---------------------------------------------------------------------------------------------------
    
    // --- 4. Funcionalidade de Criação de Post ---

    // Abrir Modal de Criação (Botão na Sidebar)
    if (openCreatePostButton && createPostModal) {
        openCreatePostButton.addEventListener('click', (e) => {
            e.preventDefault();
            openModal(createPostModal);
        });
    }

    // Fechar Modal de Criação
    if (closeCreatePostButton) {
        closeCreatePostButton.addEventListener('click', () => closeModal(createPostModal));
    }
    
    // Trigger para abrir a seleção de arquivo ao clicar na caixa de upload
    if (createUploadBox) {
        createUploadBox.addEventListener('click', () => createFileInput.click());
    }

    // Preview da imagem de Criação
    if (createFileInput) {
        createFileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (event) => { 
                    createImagePreview.src = event.target.result;
                    createImagePreview.style.display = 'block';
                    createUploadBox.style.display = 'none'; // Esconde a caixa de upload
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Submissão do Formulário de Criação (Publicar)
    if (createPostForm) {
        createPostForm.addEventListener('submit', function(e) {
            e.preventDefault(); 
            
            const legenda = createCaptionInput.value.trim();
            const imagem = createFileInput.files[0];

            if (!imagem) {
                alert("Por favor, selecione uma imagem para postar.");
                return;
            }

            // SIMULAÇÃO DE POSTAGEM
            console.log('Novo Post Enviado (Simulação):', {
                legenda: legenda,
                imagem: imagem ? imagem.name : 'Nenhuma imagem selecionada'
            });
            
            alert('Postagem criada com sucesso!');
            
            // Limpa e fecha o modal
            createPostForm.reset();
            createImagePreview.style.display = 'none';
            createUploadBox.style.display = 'flex'; // Reexibe a caixa
            closeModal(createPostModal);
        });
    }

    // ---------------------------------------------------------------------------------------------------
    
    // --- 5. Funcionalidade de Visualização de Post ---

    // Fechar Modal de Visualização
    if (closeViewPostButton) {
        closeViewPostButton.addEventListener('click', () => closeModal(viewPostModal));
    }

    // Abrir Modal ao clicar em qualquer item da grade (.post-item)
    postItems.forEach(item => {
        item.addEventListener('click', function() {
            const imgElement = item.querySelector('img');
            if (imgElement) {
                // Carrega a imagem clicada no modal de visualização
                document.getElementById('viewer-img').src = imgElement.src;
                openModal(viewPostModal);
            }
        });
    });

    // ---------------------------------------------------------------------------------------------------

    // --- 6. Fechar Modais ao Clicar no Overlay ---
    window.addEventListener('click', function(event) {
        if (event.target === editModal) {
            closeModal(editModal);
        }
        if (event.target === createPostModal) {
            closeModal(createPostModal);
        }
        if (event.target === viewPostModal) {
            closeModal(viewPostModal);
        }
    });

});