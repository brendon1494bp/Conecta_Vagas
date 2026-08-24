document.querySelectorAll('.password-toggle').forEach(button => {
  button.addEventListener('click', () => {
    const input = button.parentElement.querySelector('input');
    const showing = input.type === 'text';
    input.type = showing ? 'password' : 'text';
    button.textContent = '\u{1F441}';
    button.setAttribute('aria-label', showing ? 'Mostrar senha' : 'Ocultar senha');
  });
});
