//let root = "file:///C:/Users/franciscogo/Documents/CONSOLIDADO/";
let root = "./";
let dados = [];
let fuse;

// carregar JSON
fetch(DATA_JSON_FILE)
  .then(res => res.json())
  .then(json => {
    dados = json;

    fuse = new Fuse(dados, {
      keys: [
        "id",
        "ultima_revisao.nome",
        "ultima_revisao.assunto",
        "ultima_revisao.obra",
        "ultima_revisao.path"
      ],
      threshold: 0.3
    });

    render(dados);
  });

// render principal (AGORA AGRUPADO EM TABELAS)
function render(lista) {
  const container = document.getElementById("tabela-container");
  container.innerHTML = "";

  const grupos = agruparPorPastas(lista);

  for (const chave in grupos) {
    const titulo = document.createElement("h3");
    const qtd = grupos[chave].length;
    titulo.textContent = `${chave || "Sem pasta definida"} (${qtd} Projetos)`;
    container.appendChild(titulo);

    const table = document.createElement("table");

    const thead = document.createElement("thead");
    const trHead = document.createElement("tr");

    ["ID", "Revisão", "Extensão", "Assunto", "Abrir"].forEach(t => {
      const th = document.createElement("th");
      th.textContent = t;
      trHead.appendChild(th);
    });

    thead.appendChild(trHead);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");

    grupos[chave].forEach(item => {
      const tr = criarLinha(item);
      tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    container.appendChild(table);
  }

  atualizarContador(lista.length);
}

// agrupamento por pasta1/2/3
function agruparPorPastas(lista) {
  const grupos = {};

  lista.forEach(item => {
    const chave = [
      item.ultima_revisao.pasta1,
      item.ultima_revisao.pasta2,
      item.ultima_revisao.pasta3
    ]
      .filter(Boolean)
      .join(" / ");

    if (!grupos[chave]) {
      grupos[chave] = [];
    }

    grupos[chave].push(item);
  });

  return grupos;
}

// cria linha da tabela
function criarLinha(item) {
  const tr = document.createElement("tr");

  const revisoes = [...new Set(item.revisoes.map(r => r.revisao))];

  const selectRev = document.createElement("select");
  revisoes.forEach(r => {
    const opt = document.createElement("option");
    opt.value = r;
    opt.textContent = r;
    selectRev.appendChild(opt);
  });

  const selectExt = document.createElement("select");

  const tdAssunto = document.createElement("td");

  const link = document.createElement("a");
  link.textContent = "Abrir";
  link.target = "_blank";

  const tdPath = document.createElement("td");

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

    selectExt.value = exts.includes("pdf") ? "pdf" : exts[0];
  }

  function atualizarLink() {
    const rev = selectRev.value;
    const ext = selectExt.value;

    const encontrado = item.revisoes.find(r =>
      r.revisao === rev && r.tipo_arquivo === ext
    );

    if (encontrado) {
      link.href = root + encontrado.path;
      tdAssunto.textContent = encontrado.assunto || "";

      const pastas = [
        encontrado.pasta1,
        encontrado.pasta2,
        encontrado.pasta3
      ];

      tdPath.textContent = pastas.filter(Boolean).join(" / ");
    } else {
      link.removeAttribute("href");
      tdAssunto.textContent = "";
      tdPath.textContent = "";
    }
  }

  // eventos
  selectRev.addEventListener("change", () => {
    atualizarExtensoes();
    atualizarLink();
  });

  selectExt.addEventListener("change", atualizarLink);

  // init
  selectRev.value = item.ultima_revisao.revisao;

  atualizarExtensoes();
  selectExt.value = item.ultima_revisao.tipo_arquivo;

  atualizarLink();

  // colunas
  const tdId = document.createElement("td");
  tdId.textContent = item.id;
  tdId.className   = item.className || ""

  const tdRev = document.createElement("td");
  tdRev.appendChild(selectRev);

  const tdExt = document.createElement("td");
  tdExt.appendChild(selectExt);

  const tdLink = document.createElement("td");
  tdLink.appendChild(link);

  tr.appendChild(tdId);
  tr.appendChild(tdRev);
  tr.appendChild(tdExt);
  tr.appendChild(tdAssunto);
  tr.appendChild(tdLink);

  return tr;
}

// contador
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

document.getElementById("btn-exportar").addEventListener("click", function () {
	prepararParaExcel();
});

function prepararParaExcel() {
	// substituir selects por texto
	document.querySelectorAll("select").forEach(select => {
		const valor = select.value;

		const span = document.createElement("span");
		span.textContent = valor;

		select.parentNode.replaceChild(span, select);
	});

	// transformar links em texto (opcional, mas recomendado)
	//document.querySelectorAll("a").forEach(link => {
	//	const texto = link.href || link.textContent;

	//	const span = document.createElement("span");
	//	span.textContent = texto;

	//	link.parentNode.replaceChild(span, link);
	//});
}


