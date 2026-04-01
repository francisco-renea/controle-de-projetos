//let root = "file:///C:/Users/franciscogo/Documents/CONSOLIDADO/";
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

    //render(dados);
    ativarTabs(dados);
    const filtrados = filtrarPorPeriodo(dados, "hoje");
    render(filtrados);
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
  ativarOrdenacaoTabelas();
}



// mapeamento id -> periodo
const mapaPeriodos = {
  "tab-todos": "todos",
  "tab-hoje": "hoje",
  "tab-7dias": "7dias",
  "tab-30dias": "30dias",
  "tab-3meses": "3meses"
};

// função de filtro
function filtrarPorPeriodo(dados, periodo) {
  if (periodo === "todos") return dados; // já resolve direto

  const hoje = new Date();
  hoje.setHours(0, 0, 0, 0);

  return dados.filter(item => {
    const dataStr = item.ultima_revisao?.verificadoEm;
    if (!dataStr) return false;

    // parsing manual (evita UTC)
    const [ano, mes, dia] = dataStr.split("-").map(Number);
    const data = new Date(ano, mes - 1, dia);
    data.setHours(0, 0, 0, 0);

    const diffMs = hoje - data;
    const diffDias = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (periodo === "hoje") {
      return diffDias === 0;
    }

    if (periodo === "7dias") {
      return diffDias >= 0 && diffDias <= 7;
    }

    if (periodo === "30dias") {
      return diffDias >= 0 && diffDias <= 30;
    }

    if (periodo === "3meses") {
      return diffDias >= 0 && diffDias <= 90;
    }

    return false;
  });
}


// ativa os botões
function ativarTabs(dados) {
  const tabs = document.querySelectorAll(".tab");

  tabs.forEach(tab => {
    tab.onclick = () => {

      // troca botão ativo
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");

      // pega período
      const periodo = mapaPeriodos[tab.id] || "todos";

      // filtra e renderiza
      const filtrados = filtrarPorPeriodo(dados, periodo);
      render(filtrados);
    };
  });
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
    //const resultado = fuse.search(termo).map(r => r.item);
    //render(resultado);
    buscar(termo)
  }
});

function buscar(query) {
	query = normalizarQuery(query);

	let termos;

	if (query.includes(";")) {
		// separação explícita (modo avançado)
		termos = query
			.split(";")
			.map(t => t.trim())
			.filter(t => t.length > 0);
	} else {
		// fallback simples
		termos = query
			.split(/\s+/) // evita múltiplos espaços
			.map(t => t.trim())
			.filter(t => t.length > 0);
	}

	let resultado = dados;

	termos.forEach(termo => {
		const fuseTemp = new Fuse(resultado, {
			keys: [
				"id",
				"ultima_revisao.nome",
				"ultima_revisao.assunto",
				"ultima_revisao.obra",
				"ultima_revisao.path"
			],
			threshold: 0.4,
			ignoreLocation: true,
			minMatchCharLength: 1
		});

		resultado = fuseTemp.search(termo).map(r => r.item);
	});

	render(resultado);
}

function normalizarQuery(query) {
	const sinonimos = {
		"ap": "apoio",
		"cx": "caixa",
		"vl": "valvula"
	};
	return query
		.split(" ")
		.map(termo => {
			let t = termo.trim().toLowerCase();
			return sinonimos[t] || t;
		})
		.join(" ");
}


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

function ativarOrdenacaoTabelas() {
  const tabelas = document.querySelectorAll("table");

  tabelas.forEach((tabela) => {
    const ths = tabela.querySelectorAll("thead th");
    const tbody = tabela.querySelector("tbody");

    const linhasOriginais = Array.from(tbody.querySelectorAll("tr"));

    ths.forEach((th, colIndex) => {
      let estado = 0;

      if (!th.dataset.label) {
        th.dataset.label = th.textContent.trim();
      }

      th.style.cursor = "pointer";

      th.addEventListener("click", () => {
        estado = (estado + 1) % 3;

        // limpa todos os headers
        ths.forEach(t => {
          t.textContent = t.dataset.label;
        });

        if (estado === 0) {
          linhasOriginais.forEach(tr => tbody.appendChild(tr));
          return;
        }

        let linhas = Array.from(tbody.querySelectorAll("tr"));

        linhas.sort((a, b) => {
          let valA = getValorCelula(a, colIndex);
          let valB = getValorCelula(b, colIndex);

          // tenta número puro
          let numA = parseFloat(valA.replace(",", "."));
          let numB = parseFloat(valB.replace(",", "."));

          if (!isNaN(numA) && !isNaN(numB)) {
            return estado === 1 ? numA - numB : numB - numA;
          }

          // tenta número no final da string
          let finalA = extrairNumeroFinal(valA);
          let finalB = extrairNumeroFinal(valB);

          if (finalA !== null && finalB !== null) {
            return estado === 1 ? finalA - finalB : finalB - finalA;
          }

          // fallback: string com ordenação natural
          return estado === 1
            ? valA.localeCompare(valB, undefined, { numeric: true, sensitivity: "base" })
            : valB.localeCompare(valA, undefined, { numeric: true, sensitivity: "base" });
        });

        linhas.forEach(tr => tbody.appendChild(tr));

        // seta visual
        th.textContent = th.dataset.label + (estado === 1 ? " ↑" : " ↓");
      });
    });
  });
}

function getValorCelula(tr, index) {
  const td = tr.children[index];

  const select = td.querySelector("select");
  if (select) {
    return select.value || "";
  }

  return td.textContent.trim();
}

function extrairNumeroFinal(str) {
  const match = str.match(/(\d+)\s*$/);
  return match ? parseInt(match[1], 10) : null;
}
