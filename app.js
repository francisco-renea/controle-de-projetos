let dados = [];
let fuse;

// carregar JSON
fetch("data.json")
  .then(res => res.json())
  .then(json => {
    dados = json;

    fuse = new Fuse(dados, {
      keys: [
        "id",
        "ultima_revisao.nome",
        "ultima_revisao.assunto",
        "ultima_revisao.obra"
      ],
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

    // revisões únicas
    const revisoes = [...new Set(item.revisoes.map(r => r.revisao))];

    // select revisão
    const selectRev = document.createElement("select");
    revisoes.forEach(r => {
      const opt = document.createElement("option");
      opt.value = r;
      opt.textContent = r;
      selectRev.appendChild(opt);
    });

    // select extensão (dinâmico)
    const selectExt = document.createElement("select");

    // assunto dinâmico
    const tdAssunto = document.createElement("td");

    // link
    const link = document.createElement("a");
    link.textContent = "Abrir";
    link.target = "_blank";

	function atualizarExtensoes() {
	  const rev = selectRev.value;

	  const exts = [
	    ...new Set(
	      item.revisoes
		.filter(r => r.revisao === rev)
		.map(r => r.tipo_arquivo)
	    )
	  ];

	  selectExt.innerHTML = "";

	  exts.forEach(e => {
	    const opt = document.createElement("option");
	    opt.value = e;
	    opt.textContent = e;
	    selectExt.appendChild(opt);
	  });

	  // PRIORIDADE PARA PDF
	  if (exts.includes("pdf")) {
	    selectExt.value = "pdf";
	  } else {
	    selectExt.value = exts[0]; // fallback
	  }
	}


    function atualizarLink() {
      const rev = selectRev.value;
      const ext = selectExt.value;

      const encontrado = item.revisoes.find(r =>
        r.revisao === rev && r.tipo_arquivo === ext
      );

      if (encontrado) {
        link.href = "file:///" + encontrado.path;
        tdAssunto.textContent = encontrado.assunto || "";
      } else {
        link.removeAttribute("href");
        tdAssunto.textContent = "";
      }
    }

    // eventos
    selectRev.addEventListener("change", () => {
      atualizarExtensoes();
      atualizarLink();
    });

    selectExt.addEventListener("change", atualizarLink);

    // inicialização com última revisão
    selectRev.value = item.ultima_revisao.revisao;

    atualizarExtensoes();
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

const tdPath = document.createElement("td");

const pastas = [
  item.ultima_revisao.pasta1,
  item.ultima_revisao.pasta2,
  item.ultima_revisao.pasta3
];

tdPath.textContent = pastas
  .filter(p => p)        // remove null/undefined
  .join(" / ");          // monta breadcrumb

tr.appendChild(tdPath);

    tr.appendChild(tdId);
    tr.appendChild(tdRev);
    tr.appendChild(tdExt);
    tr.appendChild(tdAssunto);
    tr.appendChild(tdLink);

    tbody.appendChild(tr);
  });
  atualizarContador(lista.length)
}

function atualizarContador(qtd) {
  const el = document.getElementById("contador");
  el.textContent = qtd + " Projetos Encontrados";
}

// busca
document.getElementById("search").addEventListener("input", function () {
  const termo = this.value;

  if (!termo) {
    render(dados);
  } else {
    const resultado = fuse.search(termo).map(r => r.item);
    render(resultado);
  }
});
