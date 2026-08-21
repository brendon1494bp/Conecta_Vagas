const filtros = [
  [document.querySelector('#ra-atual'), document.querySelector('#escola-atual')],
  [document.querySelector('#ra-desejada'), document.querySelector('#escola-desejada')]
];
let filtrosCarregando = 0;
filtros.forEach(([ra, escola]) => {
  if (!ra || !escola) return;
  const carregar = async () => {
    filtrosCarregando += 1;
    escola.disabled = true;
    try {
      const resposta = await fetch(`/api/escolas?ra_id=${ra.value}`);
      const escolas = await resposta.json();
      const selecionada = escola.dataset.selected;
      escola.innerHTML = '<option value="" selected disabled>Selecione a escola</option>' + escolas.map(item => `<option value="${item.id}" ${String(item.id) === selecionada ? 'selected' : ''}>${item.nome}</option>`).join('');
    } finally {
      escola.disabled = false;
      filtrosCarregando -= 1;
    }
  };
  ra.addEventListener('change', carregar);
  carregar();
});
document.querySelector('#solicitacao-form')?.addEventListener('submit', event => {
  if (filtrosCarregando > 0) {
    event.preventDefault();
    alert('Aguarde o carregamento das escolas e tente novamente.');
  }
});