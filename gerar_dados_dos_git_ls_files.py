import csv
import os
import re
import argparse
import html

parser = argparse.ArgumentParser(description="Ler a saida do git ls-files e organiza os dados em csv")

parser.add_argument("input", help="Arquivo de entrada")
parser.add_argument("output", help="Arquivo de saída")

args = parser.parse_args()

INPUT = args.input
OUTPUT = args.output

print("Entrada:", INPUT)
print("Saída:", OUTPUT)


def buscar_assunto(nome, caminho_csv="assunto.csv"):
    with open(caminho_csv, newline='', encoding='cp1252') as f:
        reader = csv.reader(f, delimiter=';')
        
        for linha in reader:
            if not linha:
                continue
            
            # primeira coluna (índice 0)
            if linha[0] == nome:
                # coluna G = índice 6
                if len(linha) > 6:
                    return linha[6]
                else:
                    return None  # linha não tem coluna suficiente

    return None  # não encontrou


def identificar_fase(texto):
    match = re.search(r"\bfase\D*0*([1-3])", texto, re.IGNORECASE)
    
    if match:
        return f"Fase {match.group(1)}"
    
    return ""

def identificar_projetista(texto):
    texto = texto.lower()

    if "canhedo" in texto:
        return "CANHEDO"
    if "enescil" in texto:
        return "ENESCIL"
    return ""

def numeroDaRevisao(revisao):
    """
    Extrai o número da revisão.
    Ex: R0a -> 0, R1 -> 1
    """
    match = re.match(r'R(\d+)', revisao, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 0


def sufixoDaRevisao(revisao):
    """
    Extrai o sufixo da revisão.
    Ex: R0a -> 'a', R1 -> None
    """
    match = re.match(r'R\d+([a-z]?)', revisao, re.IGNORECASE)
    if match:
        return match.group(1) if match.group(1) != "" else None
    return ""

def marcarNovoEVelho(dados):
    revisoes_por_nome = {}

    # 1. Descobre a maior revisão por nome
    for info in dados:
        nome = info["nome"] + (info["revisao_sufixo"] or "")

        rev_num = info.get("revisao_numero", 0)

        if nome not in revisoes_por_nome:
            revisoes_por_nome[nome] = rev_num
        else:
            if rev_num > revisoes_por_nome[nome]:
                revisoes_por_nome[nome] = rev_num

    # 2. Marca como NOVO ou DESATUALIZADO
    for info in dados:
        nome = info["nome"] + (info["revisao_sufixo"] or "")
        rev_num = info.get("revisao_numero", 0)

        if rev_num == revisoes_por_nome[nome]:
            info["revisao_status"] = "NOVO"
        else:
            info["revisao_status"] = "DESATUALIZADO"

    return dados



def extrair_pastas(caminho: str, max_pastas: int = 10) -> dict:
    # separa pelo separador "/"
    partes = caminho.split("/")
    
    # remove o arquivo (última parte) se tiver extensão
    if "." in partes[-1]:
        partes = partes[:-1]
    
    resultado = {}

    for i in range(max_pastas):
        chave = f"pasta{i+1}"
        if i < len(partes):
            resultado[chave] = partes[i]
        else:
            resultado[chave] = None  # ou "" se preferir
    return resultado



def analisar_nome(path):
    base = os.path.basename(path)

    nome_sem_ext, ext = os.path.splitext(base)
    tipo_arquivo = ext.replace(".", "")
    partes_ponto = nome_sem_ext.split(".")
    revisao = partes_ponto[-1] if len(partes_ponto) > 1 else ""
    principal = ".".join(partes_ponto[:-1]) if len(partes_ponto) > 1 else nome_sem_ext

    pagina = ""
    if "_" in principal:
        principal, pagina = principal.split("_", 1)

    partes = principal.split("-")

    tipo_doc = partes[0] if len(partes) > 0 else ""
    obra = partes[1] if len(partes) > 1 else ""
    trecho = partes[2] if len(partes) > 2 else ""
    codigo = partes[3] if len(partes) > 3 else ""
    materia_raw = partes[4] if len(partes) > 4 else ""

    materia = ""
    materia_num = ""

    if materia_raw:
        m = re.match(r"([A-Za-z]+)(\d+)", materia_raw)
        if m:
            materia = m.group(1)
            materia_num = m.group(2)
        else:
            materia = materia_raw

    nome_padrao = nome_sem_ext.rsplit(".",1)[0]
    nome_padrao = nome_padrao.replace('_','/')
    assunto = buscar_assunto(nome_padrao)
    projetista = identificar_projetista(path)
    fase = identificar_fase(path)
    revisao_numero = numeroDaRevisao(revisao)
    revisao_sufixo = sufixoDaRevisao(revisao)
    obj = {
        "assunto": assunto,
        "nome": nome_padrao,
        "fase": fase,
        "projetista": projetista,
        "path": path,
        "tipo_doc": tipo_doc,
        "obra": obra,
        "trecho": trecho,
        "codigo": codigo,
        "materia": materia,
        "materia_num": materia_num,
        "pagina": pagina,
        "revisao": revisao,
        "revisao_numero": revisao_numero,
        "revisao_sufixo": revisao_sufixo,
        "tipo_arquivo": tipo_arquivo
    }
    obj |= extrair_pastas(path,10);
    return obj


with open(INPUT, encoding="utf-8-sig") as f:
    linhas = f.readlines()
dados = []
for linha in linhas:
    linha = linha.strip()
    if not linha:
        continue
    path = linha.strip()
    info = analisar_nome(path)
    dados.append(info)

dados = marcarNovoEVelho(dados)


with open(OUTPUT, "w", newline="", encoding="utf-8-sig") as csvfile:
    writer = csv.writer(csvfile,delimiter=';')

    # cabeçalho
    writer.writerow([
        "path",
        "assunto",
        "nome",
        "fase",
        "projetista",
        "tipo_doc",
        "obra",
        "trecho",
        "codigo",
        "materia",
        "materia_num",
        "pagina",
        "revisao",
        "rev_num",
        "rev_suf",
        "revisao_status",
        "tipo_arquivo",
        "pasta1",
        "pasta2",
        "pasta3",
        "pasta4",
        "pasta5",
        "pasta6",
        "pasta7",
        "pasta8",
        "pasta9",
        "pasta10"
    ])

    for info in dados:
        writer.writerow([
            info["path"],
            info["assunto"],
            info["nome"],
            info["fase"],
            info["projetista"],
            info["tipo_doc"],
            info["obra"],
            info["trecho"],
            info["codigo"],
            info["materia"],
            info["materia_num"],
            info["pagina"],
            info["revisao"],
            info["revisao_numero"],
            info["revisao_sufixo"],
            info["revisao_status"],
            info["tipo_arquivo"],
            info["pasta1"],
            info["pasta2"],
            info["pasta3"],
            info["pasta4"],
            info["pasta5"],
            info["pasta6"],
            info["pasta7"],
            info["pasta8"],
            info["pasta9"],
            info["pasta10"]
        ])

print("CSV gerado:", OUTPUT)





############# CRIAR HTML
campos = [
    "path",
    "assunto",
    "nome",
    "fase",
    "projetista",
    "tipo_doc",
    "obra",
    "trecho",
    "codigo",
    "materia",
    "materia_num",
    "pagina",
    "revisao",
    "revisao_numero",
    "revisao_sufixo",
    "revisao_status",
    "tipo_arquivo",
    "pasta1",
    "pasta2",
    "pasta3",
    "pasta4",
    "pasta5",
    "pasta6",
    "pasta7",
    "pasta8",
    "pasta9",
    "pasta10"
]

with open(OUTPUT.replace(".csv", ".html"), "w", encoding="utf-8") as f:
    f.write("""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Tabela</title>
<link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
<script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
<style>
table { border-collapse: collapse; font-family: Arial; font-size: 12px; }
th, td { border: 1px solid #ccc; padding: 4px 8px; }
th { background: #eee; }

<style>
    table {
        border-collapse: collapse;
    }

    th, td {
        white-space: nowrap;      /* impede quebra de linha */
        padding: 4px 8px;
    }
</style>
</style>
</head>
<body>
<table id="minhaTabela" class="display">
<thead>
<tr>
""")

    # Cabeçalho
    for campo in campos:
        f.write(f"<th>{campo}</th>")
    
    f.write("</tr></thead><tbody>")

    # Linhas
    for info in dados:
        f.write("<tr>")
        for campo in campos:
            valor = info.get(campo, "")

            if campo == "path" and valor:
                valor_esc = html.escape(str(valor))
                cell = f'<a href="C:/Users/franciscogo/Documents/CONSOLIDADO/{valor_esc}" target="_blank">{valor_esc}</a>'
            else:
                cell = html.escape(str(valor))

            f.write(f"<td>{cell}</td>")
        
        f.write("</tr>")

    f.write("""
</tbody>
</table>
<script>
<script>
window.addEventListener('load', function () {

    // adiciona inputs de filtro no header
    $('#minhaTabela thead th').each(function () {
        var title = $(this).text();
        $(this).html(title + '<br><input type="text" placeholder="Filtrar" />');
    });

    // inicializa DataTable (UMA VEZ SÓ)
    var table = $('#minhaTabela').DataTable({
        pageLength: 100,
        lengthMenu: [
            [10, 25, 50, 100, -1],
            [10, 25, 50, 100, "Todos"]
        ]
    });

    // aplica filtro por coluna
    table.columns().every(function () {
        var that = this;

        $('input', this.header()).on('keyup change', function () {
            if (that.search() !== this.value) {
                that.search(this.value).draw();
            }
        });
    });

});
</script>
</body>
</html>
""")

print("HTML gerado:", OUTPUT.replace(".csv", ".html"))
