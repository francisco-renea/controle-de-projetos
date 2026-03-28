let dados = [];
let fuse;

// carregar JSON
fetch('data.json')
  .then(res => res.json())
  .then(json => {
    dados = json;

    fuse = new Fuse(dados, {
      keys: ['path', 'assunto', 'nome', 'fase'],
      threshold: 0.3
    });

    render(dados);
  });

// render tabela
function render(lista) {
  const tbody = document.querySelector("#tabela tbody");
  tbody.innerHTML = "";

  lista.forEach(item => {
    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td><a href="file:///${item.path}" target="_blank">${item.path}</a></td>
      <td>${item.assunto}</td>
      <td>${item.nome}</td>
      <td>${item.fase}</td>
    `;

    tbody.appendChild(tr);
  });
}

// busca
document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("search");

  input.addEventListener("input", function () {
    const termo = this.value;

    if (!termo) {
      render(dados);
    } else {
      const resultado = fuse.search(termo).map(r => r.item);
      render(resultado);
    }
  });
});
