
//  IMPACTA - Script principal


document.addEventListener("DOMContentLoaded", () => {
  //  Seleciona todos os botões de curtir
  const likeButtons = document.querySelectorAll(".like-btn");

  likeButtons.forEach((btn) => {
    const countSpan = btn.querySelector(".count");

    btn.addEventListener("click", () => {
      const isLiked = btn.classList.toggle("liked");
      let currentCount = parseInt(countSpan.textContent);

      // Atualiza número de curtidas
      if (isLiked) {
        countSpan.textContent = currentCount + 1;
        createFloatingHeart(btn);
      } else {
        countSpan.textContent = currentCount - 1;
      }
    });
  });
});

/**
 * Cria um coração flutuante ao clicar no botão 
 */
function createFloatingHeart(button) {
  const heart = document.createElement("span");
  heart.textContent = "❤️";
  heart.classList.add("floating-heart");
  button.appendChild(heart);

  // Remove após a animação
  setTimeout(() => {
    heart.remove();
  }, 800);
}
