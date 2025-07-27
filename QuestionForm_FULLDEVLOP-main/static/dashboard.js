document.addEventListener('DOMContentLoaded', () => {
  const btnCopiar = document.getElementById('btnCopiarLink');
  const inputPesquisa = document.getElementById('pesquisaNome');
  const listaRespostas = document.getElementById('listaRespostas');

  // Botão de copiar link
  if (btnCopiar) {
    btnCopiar.addEventListener('click', copiarLink);
  }

  // Inicia todas as respostas recolhidas
  listaRespostas?.querySelectorAll('.card-body').forEach(body => {
    body.style.display = 'none';
  });

  // Toggle expandir/recolher
  listaRespostas?.querySelectorAll('.card-header').forEach(header => {
    header.addEventListener('click', () => {
      const card = header.parentElement;
      const body = card.querySelector('.card-body');
      const seta = header.querySelector('.seta');

      if (body.style.display === 'block') {
        body.style.display = 'none';
        seta.style.transform = 'rotate(0deg)';
      } else {
        body.style.display = 'block';
        seta.style.transform = 'rotate(90deg)';
      }
    });
  });

  // Filtro por nome
  inputPesquisa?.addEventListener('input', () => {
    const filtro = inputPesquisa.value.toLowerCase();
    listaRespostas?.querySelectorAll('.resposta-card').forEach(card => {
      const nome = card.getAttribute('data-nome');
      if (nome.includes(filtro)) {
        card.style.display = 'flex';
      } else {
        card.style.display = 'none';
      }
    });
  });
});

// Função para gerar link e copiar
function copiarLink() {
  fetch('/api/gerar-link', {
    method: 'POST'
  })
  .then(response => response.json())
  .then(data => {
    navigator.clipboard.writeText(data.link)
      .then(() => alert("Link copiado para a área de transferência!"))
      .catch(err => alert("Erro ao copiar: " + err));
  })
  .catch(error => {
    alert("Erro ao gerar o link: " + error);
  });
}
