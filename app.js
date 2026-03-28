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



function render(lista) {
  const tbody = document.querySelector("#tabela tbody");
  tbody.innerHTML = "";

  lista.forEach(item => {
    const tr = document.createElement("tr");

    // extrair revisões únicas
    const revisoes = [...new Set(item.revisoes.map(r => r.revisao))];

    // extrair extensões únicas
    const extensoes = [...new Set(item.revisoes.map(r => r.tipo_arquivo))];

    // selects
    const selectRev = document.createElement("select");
    revisoes.forEach(r => {
      const opt = document.createElement("option");
      opt.value = r;
      opt.textContent = r;
      selectRev.appendChild(opt);
    });

    const selectExt = document.createElement("select");
    extensoes.forEach(e => {
      const opt = document.createElement("option");
      opt.value = e;
      opt.textContent = e;
      selectExt.appendChild(opt);
    });

    // link
    const link = document.createElement("a");
    link.textContent = "Abrir";

    function atualizarLink() {
      const rev = selectRev.value;
      const ext = selectExt.value;

      const encontrado = item.revisoes.find(r =>
        r.revisao === rev && r.tipo_arquivo === ext
      );

      if (encontrado) {
        link.href = "file:///" + encontrado.path;
      } else {
        link.removeAttribute("href");
      }
    }

    // eventos
    selectRev.addEventListener("change", atualizarLink);
    selectExt.addEventListener("change", atualizarLink);

    // inicializar com ultima revisão
    selectRev.value = item.ultima_revisao.revisao;
    selectExt.value = item.ultima_revisao.tipo_arquivo;

    atualizarLink();

    // montar linha
    const tdId = document.createElement("td");
    tdId.textContent = item.id;

    const tdRev = document.createElement("td");
    tdRev.appendChild(selectRev);

    const tdExt = document.createElement("td");
    tdExt.appendChild(selectExt);

    const tdLink = document.createElement("td");
    tdLink.appendChild(link);

    tr.appendChild(tdId);
    tr.appendChild(tdRev);
    tr.appendChild(tdExt);
    tr.appendChild(tdLink);

    tbody.appendChild(tr);
  });

fuse = new Fuse(dados, {
  keys: [
    'id',
    'ultima_revisao.nome',
    'ultima_revisao.assunto',
    'ultima_revisao.obra'
  ],
  threshold: 0.3
});
}
