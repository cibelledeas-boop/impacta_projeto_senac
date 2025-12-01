// JS para funcionalidades do direct
// Exemplo: enviar mensagem, trocar conversa ativa, etc.

const form = document.querySelector('.chat-input');
if(form) {
  form.addEventListener('submit', function(e) {
    e.preventDefault();
    const input = form.querySelector('input');
    if(input.value.trim()) {
      // Adiciona mensagem enviada
      const chat = document.querySelector('.chat-mensagens');
      const div = document.createElement('div');
      div.className = 'mensagem enviada';
      div.innerHTML = `<span>Você:</span> ${input.value}`;
      chat.appendChild(div);
      input.value = '';
      chat.scrollTop = chat.scrollHeight;
    }
  });
}
