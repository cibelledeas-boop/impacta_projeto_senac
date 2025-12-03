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

