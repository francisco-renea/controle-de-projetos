import subprocess
import os
from collections import defaultdict
import re


result = subprocess.run(
        #["git", "diff", "--name-status","HEAD~1", "HEAD"],
    ["git", "ls-files"],
    capture_output=True,
    text=True,
    check=True,
    encoding="utf-8", 
    cwd="."
)

saida = result.stdout
linhas = saida.splitlines()


def parse_linha(linha):
    #status = linha[:2]
    #path = linha[2:].strip().strip('"')
    status = linha[:1]
    path = linha[0:].strip().strip('"')
    return status, path


def arvore():
    return defaultdict(arvore)

tree = arvore()

def inserir(tree, path, status):
    partes = path.strip("/").split("/")
    node = tree
    for p in partes[:-1]:
        node = node[p]
    node[partes[-1]] = {"__status__": status}

for linha in linhas:
    status, path = parse_linha(linha)
    inserir(tree, path, status)


def classe_status(status):
    if status == "A":
        return "novo"
    elif status.strip() == "M":
        return "modificado"
    elif status.strip() == "D":
        return "deletado"
    else:
        return "outro"


def render(node):
    html = "<ul>"

    # separa pastas e arquivos
    pastas = []
    arquivos = []

    for k, v in node.items():
        if isinstance(v, dict) and "__status__" not in v:
            pastas.append((k, v))
        else:
            arquivos.append((k, v))

    # ordena alfabeticamente
    pastas.sort()
    arquivos.sort()

    # render pastas primeiro
    for nome, conteudo in pastas:
        html += f"<li><strong>📁 {nome}</strong>"
        html += render(conteudo)
        html += "</li>"

    # depois arquivos
    for nome, conteudo in arquivos:
        status = conteudo["__status__"]
        classe = classe_status(status)
        print(nome)
        html += f'<li><div class="{classe}">{status} 📄 {nome}</div></li>'

    html += "</ul>"
    return html

def analisar_nome(nome_arquivo):
    base = os.path.basename(nome_arquivo)

    # extensão (tipo)
    nome_sem_ext, ext = os.path.splitext(base)
    tipo = ext.replace(".", "")

    # revisão (último . antes da extensão)
    partes_ponto = nome_sem_ext.split(".")
    revisao = partes_ponto[-1] if len(partes_ponto) > 1 else ""

    # parte principal (antes da revisão)
    principal = ".".join(partes_ponto[:-1]) if len(partes_ponto) > 1 else nome_sem_ext

    # página (_003)
    pagina = ""
    if "_" in principal:
        principal, pagina = principal.split("_", 1)

    # dividir por "-"
    partes = principal.split("-")

    tipo_doc = partes[0] if len(partes) > 0 else ""
    obra = partes[1] if len(partes) > 1 else ""
    trecho = partes[2] if len(partes) > 2 else ""
    codigo = partes[3] if len(partes) > 3 else ""
    materia_raw = partes[4] if len(partes) > 4 else ""

    # matéria separando letra e número (ex: G12)
    materia = ""
    materia_num = ""
    if materia_raw:
        m = re.match(r"([A-Za-z]+)(\d+)", materia_raw)
        if m:
            materia = m.group(1)
            materia_num = m.group(2)
        else:
            materia = materia_raw

    return {
        "tipo_doc": tipo_doc,      # DE
        "obra": obra,              # SPM00021D
        "trecho": trecho,          # 115.117
        "codigo": codigo,          # 925
        "materia": materia,        # G
        "materia_num": materia_num,# 12
        "pagina": pagina,          # 003
        "revisao": revisao,        # R1a
        "tipo_arquivo": tipo       # pdf
    }



def flatten(node, caminho=None):
    if caminho is None:
        caminho = []

    linhas = []

    for nome, conteudo in node.items():
        if isinstance(conteudo, dict) and "__status__" not in conteudo:
            # pasta → desce na árvore
            linhas.extend(flatten(conteudo, caminho + [nome]))
        else:
            # arquivo
            status = conteudo["__status__"]
            linhas.append((caminho, nome, status))

    return linhas

def render_table(tree):
    linhas = flatten(tree)

    # descobrir profundidade máxima de pastas
    max_nivel = max(len(c[0]) for c in linhas) if linhas else 0

    html = "<table border='1'>"

    # cabeçalho
    html += "<tr>"
    for i in range(max_nivel):
        html += f"<th>Pasta {i+1}</th>"
    html += "<th>Arquivo</th><th>Status</th>"
    html += """
    <th>Tipo</th>
    <th>Obra</th>
    <th>Trecho</th>
    <th>Código</th>
    <th>Matéria</th>
    <th>Matéria Nº</th>
    <th>Página</th>
    <th>Revisão</th>
    <th>Arquivo</th>
    </tr>
    """

    # linhas
    for caminho, nome, status in linhas:
        classe = classe_status(status)

        html += "<tr>"

        # pastas (preenche vazio se necessário)
        for i in range(max_nivel):
            if i < len(caminho):
                html += f"<td>{caminho[i]}</td>"
            else:
                html += "<td></td>"


        html += f"<td>{nome}</td>"
        html += f'<td class="{classe}">{status}</td>'
        info = analisar_nome(nome)
        html += f"<td>{info['tipo_doc']}</td>"
        html += f"<td>{info['obra']}</td>"
        html += f"<td>{info['trecho']}</td>"
        html += f"<td>{info['codigo']}</td>"
        html += f"<td>{info['materia']}</td>"
        html += f"<td>{info['materia_num']}</td>"
        html += f"<td>{info['pagina']}</td>"
        html += f"<td>{info['revisao']}</td>"
        html += f"<td>{info['tipo_arquivo']}</td>"

        html += "</tr>"

    html += "</table>"
    return html

html = f"""
<html>
<body>
<style>
ul,li {{list-style-type:none}}
.novo {{ color: green; }}
.modificado {{ color: blue; }}
</style>
<h1>Status do Git</h1>
{render_table(tree)}
</body>
</html>
"""

OUTPUT = "relatorio.html"
with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(html)

os.startfile(OUTPUT)
