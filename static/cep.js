document.querySelectorAll('[data-address-target]').forEach(input => {
  let consultaAtual;
  const endereco = document.querySelector(input.dataset.addressTarget);
  const status = document.querySelector(input.dataset.addressStatus);

  async function consultarCep() {
    const cep = input.value.replace(/\D/g, '');
    if (!cep) {
      status.textContent = '';
      return;
    }
    if (cep.length !== 8) {
      status.textContent = 'Digite um CEP com 8 números.';
      status.className = 'form-text text-danger';
      return;
    }

    consultaAtual?.abort();
    consultaAtual = new AbortController();
    status.textContent = 'Buscando endereço...';
    status.className = 'form-text text-muted';

    try {
      const resposta = await fetch(
        `https://brasilapi.com.br/api/cep/v2/${cep}`,
        { signal: consultaAtual.signal },
      );
      if (!resposta.ok) throw new Error('CEP não encontrado');
      const dados = await resposta.json();
      const partes = [dados.street, dados.neighborhood]
        .filter(Boolean);
      const localidade = [dados.city, dados.state]
        .filter(Boolean)
        .join(' - ');
      if (localidade) partes.push(localidade);
      partes.push(`CEP: ${dados.cep || cep}`);
      endereco.value = partes.join(', ');
      status.textContent = 'Endereço preenchido automaticamente.';
      status.className = 'form-text text-success';
    } catch (erro) {
      if (erro.name === 'AbortError') return;
      status.textContent = 'Não foi possível localizar este CEP. Preencha o endereço manualmente.';
      status.className = 'form-text text-danger';
    }
  }

  input.addEventListener('blur', consultarCep);
  input.addEventListener('keydown', event => {
    if (event.key === 'Enter') {
      event.preventDefault();
      consultarCep();
    }
  });

  if (input.value.replace(/\D/g, '').length === 8) consultarCep();
});
