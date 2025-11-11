document.addEventListener("DOMContentLoaded", () => {
  const likeBtn = document.querySelector(".like-btn");
  const likeCount = likeBtn.querySelector(".count");

  likeBtn.addEventListener("click", () => {
    const liked = likeBtn.classList.toggle("liked");
    let count = parseInt(likeCount.textContent, 10);
    likeCount.textContent = liked ? count + 1 : count - 1;
  });

  document.querySelector(".donate").addEventListener("click", () => {
    alert("Obrigado por sua doação!");
  });
});
