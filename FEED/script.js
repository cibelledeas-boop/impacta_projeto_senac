// IMPACTA - Script principal

document.addEventListener("DOMContentLoaded", () => {
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

