// JS para funcionalidades de notificações
// Exemplo: marcar como lida, remover notificação, etc.

const notificacoes = document.querySelectorAll('.notificacoes-lista li');
notificacoes.forEach(li => {
  li.addEventListener('click', () => {
    li.style.background = '#e0f2fe';
    setTimeout(() => li.style.background = '', 800);
  });
});
