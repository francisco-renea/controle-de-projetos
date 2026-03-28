from pathlib import Path
import json 
import os 
import re 

import argparse
parser = argparse.ArgumentParser(description="Ler a saida do git ls-files e organiza os dados em csv")
parser.add_argument("input", help="Arquivo de entrada")
args = parser.parse_args()
INPUT = args.input


arquivo = Path(INPUT).resolve()
currentPasta = arquivo.parent.name

dataPath = os.path.expanduser("~/system/data.json")
enviadosPath = INPUT #os.path.expanduser("~/Documents/PROJETOS-PARA-ENGENHEIROS/ALVARO/03-Projeto de Drenagem/enviados.json")

with open(dataPath, "r", encoding="utf-8") as f:
    dados = json.load(f)

with open(enviadosPath, "r", encoding="utf-8") as f:
    enviados = json.load(f)


def getRevisao(path):
    matches = re.findall(r'R[^.]*', path)
    return matches[-1] if matches else ""


def getId(path):
    nome = path.split("/")[-1]
    
    match = re.match(r"(.*)\.R[^.]*\.(.+)", nome)
    
    if match:
        return match.group(1)  # sem revisão
    return nome

filtrados = []
for e in enviados:
    i = getId(e)
    r = getRevisao(e)
    filtrados.append({
        "id": i,
        "re" : r,
        "path" : e
        })

vistos = set()
unicos = []
faltaEnviar = []

for doc in filtrados:
    if doc["id"] not in vistos:
        unicos.append(doc)
        vistos.add(doc["id"])


text = "<table>"
text += f"<caption>{currentPasta}</caption>"
text += "<tbody>"
text += "<th><td>Antigo</td><td>Novo</td><td>pasta</td></th>"
count = 0
for e in unicos:
    i = e["id"].replace("_","/")
    r = e["re"]
    p = e["path"]
    for doc in dados:
        doc_id = doc["id"].replace("_","/")
        doc_re = doc["ultima_revisao"]["revisao"]
        doc_path = doc["ultima_revisao"]["path"]
        if i == doc_id and r < doc_re:
            faltaEnviar.append(f'C:Users/franciscogo/Documents/Consolidado/{doc_path}')
            count += 1
            text += f'<tr><td>{count}</td><td><a href="file:///C:Users/franciscogo/Documents/Consolidado/{p}">{i}.{r}</a></td><td><a href="file:///C:Users/franciscogo/Documents/Consolidado/{doc_path}">{doc_id}.{doc_re}</a></td><td>{doc_path}</td></tr>'
text += "<tbody>"
text += "</table>"
#print(text)


with open("faltaEnviar.html","w",encoding="utf-8") as f:
    f.write(text)

with open("faltaEnviar.json","w",encoding="utf-8") as f:
    json.dump(faltaEnviar,f,ensure_ascii=False,indent=4)
