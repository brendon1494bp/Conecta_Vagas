function cpfValido(valor) {
  const cpf = valor.replace(/\D/g, '');
  if (cpf.length !== 11 || /^([0-9])\1{10}$/.test(cpf)) return false;
  for (let tamanho = 9; tamanho <= 10; tamanho += 1) {
    let soma = 0;
    for (let indice = 0; indice < tamanho; indice += 1) soma += Number(cpf[indice]) * (tamanho + 1 - indice);
    let digito = (soma * 10) % 11;
    if (digito === 10) digito = 0;
    if (digito !== Number(cpf[tamanho])) return false;
  }
  return true;
}

document.querySelectorAll('[data-mask="cpf"]').forEach(input => {
  input.addEventListener('input', () => {
    input.value = input.value.replace(/\D/g, '').slice(0, 11)
      .replace(/(\d{3})(\d)/, '$1.$2')
      .replace(/(\d{3})(\d)/, '$1.$2')
      .replace(/(\d{3})(\d{1,2})$/, '$1-$2');
    input.setCustomValidity(input.value && !cpfValido(input.value) ? 'Informe um CPF válido.' : '');
  });
});

document.querySelectorAll('[data-mask="telefone"]').forEach(input => input.addEventListener('input', () => {
  input.value = input.value.replace(/\D/g, '').slice(0, 11)
    .replace(/^([\d]{2})([\d]{5})([\d]{4})$/, '($1) $2-$3')
    .replace(/^([\d]{2})([\d]{4})([\d]{4})$/, '($1) $2-$3');
}));

document.querySelectorAll('[data-mask="cep"]').forEach(input => input.addEventListener('input', () => {
  input.value = input.value.replace(/\D/g, '').slice(0, 8)
    .replace(/(\d{5})(\d)/, '$1-$2');
}));

document.querySelectorAll('#cpf-form').forEach(form => form.addEventListener('submit', event => {
  const cpf = form.querySelector('[data-mask="cpf"]');
  if (cpf && !cpfValido(cpf.value)) {
    cpf.setCustomValidity('Informe um CPF válido.');
    cpf.reportValidity();
    event.preventDefault();
  }
}));
