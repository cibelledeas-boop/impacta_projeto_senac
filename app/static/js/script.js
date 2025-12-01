// IMPACTA - Script principal

document.addEventListener("DOMContentLoaded", () => {
    // =====================
    // 🔔 ABA FLUTUANTE DE NOTIFICAÇÕES
    // =====================
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
  // =====================
  // ❤️ BOTÃO LIKE
  // =====================
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

  // =====================
  // 🟦 BOTÃO CRIAR POST (MODAL)
  // =====================
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
  };

  // =====================
  // Alternar botão Entrar/Direct (simulação de login)
  // =====================
  const btnEntrar = document.getElementById("btn-entrar");
  const btnDirect = document.getElementById("btn-direct");

  // Simulação: usuário está logado (troque para false para ver o botão Entrar)
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

  // =====================
  // 💬 BOTÃO FLUTUANTE CHATBOT
  // =====================
  const chatbotBtn = document.getElementById("chatbot-float-btn");
  const chatbotBox = document.getElementById("chatbot-box");
  const closeChatbot = document.getElementById("close-chatbot");

  if (chatbotBtn && chatbotBox) {
    chatbotBtn.onclick = () => {
      chatbotBox.style.display = "flex";
      chatbotBtn.style.display = "none";
    };
  }
  if (closeChatbot && chatbotBox && chatbotBtn) {
    closeChatbot.onclick = () => {
      chatbotBox.style.display = "none";
      chatbotBtn.style.display = "flex";
    };
  }
});

// =====================
// ❤️ Coração flutuante
// =====================
function createFloatingHeart(button) {
  const heart = document.createElement("span");
  heart.textContent = "❤️";
  heart.classList.add("floating-heart");
  button.appendChild(heart);

  setTimeout(() => {
    heart.remove();
  }, 800);
}

