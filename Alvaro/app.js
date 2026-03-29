let dadosLocal;
let isLoaded = false;
fetch("data.json").then(res => res.json()).then(json => { dadosLocal = json; isLoaded = true; onDadosCarregados(dados, dadosLocal); })

function onDadosCarregados()
{
}


function colocarClassName()
{
	dados.forEach(novo => dadosLocal.forEach( velho => { 
		if(novo.id == velho.id) 
		{
			let className =getClassName(novo,velho);
			novo.className = className;
			velho.className = className;
		}
	}))
}

function getClassName(novo,velho)
{
	let text = "";
	let n = novo.ultima_revisao.revisao;
	let v = velho.ultima_revisao.revisao;
	if(n > v)
            text = "desatualizado";
	else if(n < v)
            text = "superatualizado";
	else if(n == v)
            text = "atualizado";
	return text;
}


function initialize() {
  const timer = setInterval(() => {
    const v1 = dados;
    const v2 = dadosLocal;

    if (v1 !== undefined && v1 !== null && v2 !== undefined && v2 !== null) {
      clearInterval(timer);
      colocarClassName();
      render(dados); 
      console.log("inicializado"); 
    }
  }, 500);
}
initialize()
