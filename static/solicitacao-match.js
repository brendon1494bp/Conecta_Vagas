const intervaloMatch = 5000;
let pollingMatchAtivo = true;
let consultaMatchEmAndamento = false;

async function verificarMatch() {
  if (!pollingMatchAtivo || consultaMatchEmAndamento) return;
  consultaMatchEmAndamento = true;

  try {
    const resposta = await fetch(
      `/api/solicitacoes/${window.solicitacaoMatchId}/match`,
      { cache: 'no-store', headers: { Accept: 'application/json' } },
    );
    if (!resposta.ok) return;

    const dados = await resposta.json();
    if (dados.matched) {
      pollingMatchAtivo = false;
      window.alert('Um match foi encontrado para sua solicitação!');
      window.location.reload();
    }
  } catch (erro) {
    // Uma falha temporária não deve interromper as próximas consultas.
  } finally {
    consultaMatchEmAndamento = false;
  }
}

verificarMatch();
window.setInterval(verificarMatch, intervaloMatch);
