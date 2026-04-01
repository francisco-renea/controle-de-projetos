import subprocess
from collections import defaultdict
from datetime import datetime
import json
import csv
import os
import re
import argparse
import html
import os


#parser = argparse.ArgumentParser(description="Ler a saida do git ls-files e organiza os dados em csv")
#parser.add_argument("input", help="Arquivo de entrada")
#parser.add_argument("output", help="Arquivo de saída")
#args = parser.parse_args()

INPUT  = "entrada.txt"
OUTPUT = "data.json"

print("Entrada:", INPUT)
print("Saída:", OUTPUT)


def obter_git_log_normalizado():
    repo_path = os.path.expanduser("~/Documents/CONSOLIDADO")
    resultado = subprocess.run(
        ["git", "log", "--name-only", '--pretty=format:%ad', "--date=short"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=repo_path
    )

    raw = resultado.stdout  # bytes

    encodings_tentativa = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "ascii"]

    for enc in encodings_tentativa:
        try:
            texto = raw.decode(enc)
            print(f"[OK] Decodificado com: {enc}")
            break
        except UnicodeDecodeError:
            continue
    else:
        raise Exception("Não foi possível decodificar saída do git")

    # normalização final (equivalente ao readlines)
    linhas = [linha.strip() for linha in texto.splitlines() if linha.strip()]

    return linhas



def ler_arquivo_seguro(path) -> str:
    encodings_tentativa = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "ASCII"]

    for enc in encodings_tentativa:
        try:
            with open(path,"r", encoding=enc) as f:
                print(f"[OK] Lido com encoding: {enc}")
                return f.readlines()
        except UnicodeDecodeError:
            continue

    raise Exception("Não foi possível decodificar o arquivo com encodings conhecidos")


def normalizar_texto(texto):
    # remove caracteres problemáticos invisíveis
    return texto.replace("\ufeff", "").strip()


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

def gerar_id(path):
    nome = path.split("/")[-1]
    
    match = re.match(r"(.*)\.R[^.]*\.(.+)", nome)
    
    if match:
        return match.group(1)  # sem revisão
    return nome

def agrupar_por_revisao(dados):
    grupos = defaultdict(list)

    for info in dados:
        id_base = gerar_id(info["path"])
        grupos[id_base].append(info)

    return grupos

def montar_estrutura(grupos):
    resultado = []

    for id_base, revisoes in grupos.items():

        # ordenar por revisão (importante)
        revisoes.sort(key=lambda x: (
            x.get("revisao_numero", 0),
            x.get("revisao_sufixo", "")
        ))

        resultado.append({
            "id": id_base,
            "revisoes": revisoes,
            "ultima_revisao": revisoes[-1]  # útil no front
        })

    return resultado


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
        "id": gerar_id(path),
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



def parse_arquivo():
    resultado = []
    data_atual = None

    linhas = obter_git_log_normalizado()

    for linha in linhas:
        linha = linha.strip()

        if not linha:
            continue

        # tenta interpretar como data
        try:
            data_atual = datetime.strptime(linha, "%Y-%m-%d").date()
            continue
        except ValueError:
            pass

        if data_atual is None:
            raise ValueError(f"Path antes de data: {linha}")

        resultado.append({
            "data": data_atual.isoformat(),
            "path": linha
        })

    return resultado


def salvar_json(dados, caminho_saida):
    import json
    with open(caminho_saida, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

def eh_excecao(texto, excecoes):
    texto = texto.lower()
    return any(exc.lower() in texto for exc in excecoes)

# execução
linhas = parse_arquivo()
dados = []
excecoes = ["final", ".py", ".js", ".html", ".css", "json"]
for linha in linhas:
    path = linha["path"]
    if eh_excecao(path, excecoes):
        continue
    info = analisar_nome(path)
    info["verificadoEm"] = linha["data"]
    dados.append(info)

dados = marcarNovoEVelho(dados)
dados = agrupar_por_revisao(dados)
dados = montar_estrutura(dados)
with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(dados,f,ensure_ascii=False,indent=2)
print(f"[OK] {len(dados)} registros processados")
