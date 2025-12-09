  // Excluir comentário via AJAX
  document.querySelectorAll('.delete-comment-form').forEach(form => {
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      const postId = form.getAttribute('data-post-id');
      const commentIdx = form.getAttribute('data-comment-idx');
      fetch(`/excluir_comentario/${postId}/${commentIdx}`, { method: 'POST' })
        .then(res => {
          if (res.ok) {
            // Remove o comentário do DOM
            form.closest('li').remove();
          }
        });
    });
  });
// IMPACTA - Script principal

document.addEventListener("DOMContentLoaded", () => {
  
    // ABA FLUTUANTE DE NOTIFICAÇÕES
    const notificacoesBtn = document.getElementById("notificacoes-btn");
    const notificacoesBox = document.getElementById("notificacoes-box");
    const closeNotificacoes = document.getElementById("close-notificacoes");

    if (notificacoesBtn && notificacoesBox) {
      notificacoesBtn.onclick = () => {
        notificacoesBox.style.display = "flex";
        notificacoesBtn.style.display = "none";
      };
    }
    if (closeNotificacoes && notificacoesBox && notificacoesBtn) {
      closeNotificacoes.onclick = () => {
        notificacoesBox.style.display = "none";
        notificacoesBtn.style.display = "inline-flex";
      };
    }
//botão like
  const likeButtons = document.querySelectorAll(".like-btn");

  likeButtons.forEach((btn) => {
    const countSpan = btn.querySelector(".count");

    btn.addEventListener("click", () => {
      const isLiked = btn.classList.toggle("liked");
      let currentCount = parseInt(countSpan.textContent);

      if (isLiked) {
        countSpan.textContent = currentCount + 1;
        createFloatingHeart(btn);
      } else {
        countSpan.textContent = currentCount - 1;
      }
    });
  });

  const overlay = document.getElementById("infoOverlay");
  const abrir = document.getElementById("abrirInfo");
  const fechar = document.getElementById("fecharInfo");

  if (abrir) {
    abrir.onclick = () => {
      overlay.style.display = "flex";
      document.body.classList.add("no-scroll");
    };
  }

  if (fechar) {
    fechar.onclick = () => {
      overlay.style.display = "none";
      document.body.classList.remove("no-scroll");
    };
  }

  overlay.onclick = (e) => {
    if (e.target === overlay) {
      overlay.style.display = "none";
      document.body.classList.remove("no-scroll");
    }
  }


  // Alternar botão Entrar/Direct (simulação de login)
  
  const btnEntrar = document.getElementById("btn-entrar");
  const btnDirect = document.getElementById("btn-direct");

  const usuarioLogado = true;

  if (btnEntrar && btnDirect) {
    if (usuarioLogado) {
      btnEntrar.style.display = "none";
      btnDirect.style.display = "inline-flex";
    } else {
      btnEntrar.style.display = "inline-flex";
      btnDirect.style.display = "none";
    }
    btnDirect.onclick = () => {
      window.location.href = "direct.html";
    };
  }


  // 💬 BOTÃO FLUTUANTE CHATBOT
  const chatbotBtn = document.getElementById("chatbot-float-btn");
  const chatbotBox = document.getElementById("chatbot-box");
  const closeChatbot = document.getElementById("close-chatbot");

  if (chatbotBtn && chatbotBox) {
    chatbotBtn.onclick = () => {
      chatbotBox.classList.add("active");
    };
  }
  if (closeChatbot && chatbotBox && chatbotBtn) {
    closeChatbot.onclick = () => {
      chatbotBox.classList.remove("active");
    };
  }

  // Função para abrir o formulário de criar post
  const abrirInfo = document.getElementById("abrirInfo");
  const infoOverlay = document.getElementById("infoOverlay");
  const fecharInfo = document.getElementById("fecharInfo");

  if (abrirInfo && infoOverlay) {
    abrirInfo.onclick = () => {
      infoOverlay.style.display = "flex";
      document.body.classList.add("no-scroll");
    };
  }
  if (fecharInfo && infoOverlay) {
    fecharInfo.onclick = () => {
      infoOverlay.style.display = "none";
      document.body.classList.remove("no-scroll");
    };
  }
  infoOverlay && (infoOverlay.onclick = (e) => {
    if (e.target === infoOverlay) {
      infoOverlay.style.display = "none";
      document.body.classList.remove("no-scroll");
    }
  });


  // Controle do campo de categoria no formulário de post
  const categoriaRadios = document.querySelectorAll('input[name="categoria"]');
  const categoriaInput = document.getElementById('categoriaInput');
  if (categoriaRadios && categoriaInput) {
    categoriaRadios.forEach(radio => {
      radio.addEventListener('change', function() {
        categoriaInput.value = this.value;
      });
      // Seleção inicial
      if (radio.checked) {
        categoriaInput.value = radio.value;
      }
    });
  }


  // Preview da imagem no formulário de post
  const fotoInput = document.getElementById('foto');
  if (fotoInput) {
    fotoInput.addEventListener('change', function(event) {
      const previewContainer = document.querySelector('.upload-container');
      let previewImg = document.getElementById('preview-img');
      if (!previewImg) {
        previewImg = document.createElement('img');
        previewImg.id = 'preview-img';
        previewImg.style.maxWidth = '120px';
        previewImg.style.maxHeight = '120px';
        previewImg.style.display = 'block';
        previewImg.style.marginTop = '10px';
        previewContainer.appendChild(previewImg);
      }
      const file = event.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
          previewImg.src = e.target.result;
          previewImg.alt = 'Prévia da imagem';
        };
        reader.readAsDataURL(file);
      } else {
        previewImg.src = '';
        previewImg.alt = '';
      }
    });
  }

  // Abrir/fechar aba de comentários (accordion)
  document.querySelectorAll('.toggle-comments-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      const postId = btn.getAttribute('data-post-id');
      const commentsDiv = document.getElementById('comments-' + postId);
      if (commentsDiv) {
        if (commentsDiv.style.display === 'none' || commentsDiv.style.display === '') {
          commentsDiv.style.display = 'block';
        } else {
          commentsDiv.style.display = 'none';
        }
      }
    });
  });
});


function createFloatingHeart(button) {
  const heart = document.createElement("span");
  heart.textContent = "❤️";
  heart.classList.add("floating-heart");
  button.appendChild(heart);

  setTimeout(() => {
    heart.remove();
  }, 800);
}

//Leaflet + OSM (Mapa Pontos de Coleta) 
window.addEventListener('DOMContentLoaded', function() {
  if (document.getElementById('mapa-coleta') && window.L) {
    var map = L.map('mapa-coleta').setView([-15.793889, -47.882778], 12); // Brasília
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap'
    }).addTo(map);
    var pontos = [
      {lat: -15.793889, lng: -47.882778, nome: 'Praça dos Três Poderes'},
      {lat: -15.800000, lng: -47.860000, nome: 'Parque da Cidade'},
      {lat: -15.780000, lng: -47.900000, nome: 'Lago Sul'},
      {lat: -15.820000, lng: -47.950000, nome: 'Taguatinga'},
      {lat: -15.730000, lng: -47.890000, nome: 'Asa Norte'}
    ];
    pontos.forEach(function(ponto) {
      L.marker([ponto.lat, ponto.lng]).addTo(map)
        .bindPopup(ponto.nome);
    });
  }
});

//Validação de categoria obrigatória no post
document.addEventListener('DOMContentLoaded', function() {
  const postForm = document.getElementById('postForm');
  if (postForm) {
    postForm.addEventListener('submit', function(e) {
      const categoriaSelecionada = document.querySelector('input[name="categoria"]:checked');
      if (!categoriaSelecionada) {
        alert('Selecione uma categoria: História, Campanha ou Item.');
        e.preventDefault();
      }
    });
  }
});

// Curtir post via AJAX
  document.querySelectorAll('.like-btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const postId = btn.getAttribute('data-post-id');
      fetch(`/curtir/${postId}`, { method: 'POST' })
        .then(res => {
          if (res.ok) {
            const countSpan = btn.querySelector('.count');
            countSpan.textContent = parseInt(countSpan.textContent) + 1;
            createFloatingHeart(btn);
          }
        });
    });
  });

// Comentar post sem recarregar e atualizar comentários dinamicamente
  document.querySelectorAll('.comment-form').forEach(form => {
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      const postId = form.getAttribute('data-post-id');
      const input = form.querySelector('input[name="comentario"]');
      const comentario = input.value.trim();
      if (!comentario) return;
      const formData = new FormData();
      formData.append('comentario', comentario);
      fetch(`/comentar/${postId}`, {
        method: 'POST',
        body: formData
      })
      .then(res => {
        if (res.ok) {
          // Mensagem de confirmação
          let msg = form.querySelector('.comment-success');
          if (!msg) {
            msg = document.createElement('span');
            msg.className = 'comment-success';
            msg.style.color = '#2ecc40';
            msg.style.fontSize = '0.95em';
            msg.style.marginLeft = '8px';
            form.appendChild(msg);
          }
          msg.textContent = 'Comentário enviado!';
          setTimeout(() => { msg.textContent = ''; }, 2000);
          // Atualiza a página para mostrar o novo comentário
          setTimeout(() => { window.location.reload(); }, 600);
        }
      });
    });
  });

// Excluir post via AJAX
  document.querySelectorAll('.delete-post-btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      if (!confirm('Tem certeza que deseja excluir este post?')) return;
      const postId = btn.getAttribute('data-post-id');
      fetch(`/excluir/${postId}`, { method: 'POST' })
        .then(res => {
          if (res.ok) {
            // Remove o post do DOM
            const article = btn.closest('article.card');
            if (article) article.remove();
          }
        });
    });
  });

// Chatbot Gemini - integração frontend
const chatbotInput = document.querySelector('.chatbot-input-area input[type="text"]');
const chatbotForm = document.querySelector('.chatbot-input-area');
const chatbotMessages = document.querySelector('.chatbot-messages');

if (chatbotForm && chatbotInput && chatbotMessages) {
  chatbotForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const userMsg = chatbotInput.value.trim();
    if (!userMsg) return;
    // Adiciona mensagem do usuário
    const userDiv = document.createElement('div');
    userDiv.className = 'chatbot-message chatbot-message-user';
    userDiv.innerHTML = `<span>${userMsg}</span>`;
    chatbotMessages.appendChild(userDiv);
    chatbotInput.value = '';
    // Chama backend Gemini
    fetch('/chatbot', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: userMsg })
    })
    .then(res => res.json())
    .then(data => {
      const botDiv = document.createElement('div');
      botDiv.className = 'chatbot-message chatbot-message-bot';
      if (data.resposta) {
        botDiv.innerHTML = `<span>${data.resposta}</span>`;
      } else if (data.erro) {
        botDiv.innerHTML = `<span style="color:#e74c3c;">${data.erro}</span>`;
      } else {
        botDiv.innerHTML = `<span>Desculpe, houve um erro inesperado.</span>`;
      }
      chatbotMessages.appendChild(botDiv);
      chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    })
    .catch(() => {
      const botDiv = document.createElement('div');
      botDiv.className = 'chatbot-message chatbot-message-bot';
      botDiv.innerHTML = `<span>Desculpe, houve um erro ao conectar à IA.</span>`;
      chatbotMessages.appendChild(botDiv);
    });
  });
}

