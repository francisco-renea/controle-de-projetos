# ===== LISTA DE FILTROS (VOCÊ PODE EDITAR) =====
FILTROS = {
        "00-Topografia"                       : "00-Topografia",
        "01-Projeto Geométrico"               : "01-Projeto Geométrico",
        "02-Projeto de Terraplenagem"         : "02-Projeto de Terraplenagem",
        "03-Projeto de Drenagem"              : "03-Projeto de Drenagem",
        "04-Projeto de Sinalização"           : "04-Projeto de Sinalização",
        "06-Projeto de Pavimentação"          : "06-Projeto de Pavimentação",
        "07-Projeto de Estruturas"            : "07-Projeto de Estruturas",
        "08-Projeto de Elétrica"              : "08-Projeto de Elétrica",
        "09-Projeto de Geotecnia"             : "09-Projeto de Geotecnia",
        "10-Projeto de Interferências"        : "(10-Interferências|10-Projeto de interferência)",
        "11-Desapropriação"                   : "11-Desapropriação",
        "12-Projeto de Desvio de Tráfego"     : "12-Projeto de Desvio de Tráfego",
        "13-Projeto de Arquitetura"           : "13-Projeto de Arquitetura",
        "16-Projeto de Paisagismo"            : "(16-Paisagismo|16-Projeto de Paisagismo)",
        "BASES DOS PÓRTICOS E SEMIPÓRTICOS"   : "BASES DOS PÓRTICOS E SEMIPÓRTICOS",
        "CALLBOX"                             : "CALLBOX",
        "ENESCIL"                             : "ENESCIL",
        "ESBOÇO PROJETOS - COMGÁS"            : "ESBOÇO PROJETOS - COMGÁS",
        "FUNCIONAL"                           : "FUNCIONAL",
        "INSTRUMENTAÇÃO FASE 03"              : "INSTRUMENTAÇÃO FASE 03",
        }

KEY = ""


import sys
import sys
import os
sys.path.append(os.path.abspath("../modules"))
ROOT = os.path.expanduser("~/Documents/CONSOLIDADO/").replace("\\","/")
import pdf
import re
import json
import argparse

parser = argparse.ArgumentParser(description="Ler a saida do git ls-files e organiza os dados em csv")

parser.add_argument("input", help="Arquivo de entrada")
parser.add_argument("output", help="Arquivo de saída")

args = parser.parse_args()

INPUT = args.input
OUTPUT = args.output

print("Entrada:", INPUT)
print("Saída:", OUTPUT)


def ler_arquivo_seguro(path) -> str:
    encodings_tentativa = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]

    for enc in encodings_tentativa:
        try:
            with open(path,"r", encoding=enc) as f:
                print(f"[OK] Lido com encoding: {enc}")
                return f.readlines()
        except UnicodeDecodeError:
            continue

    raise Exception("Não foi possível decodificar o arquivo com encodings conhecidos")




def verificar(path, filtro):
    return re.search(filtro, path, re.IGNORECASE) is not None


def escolher_filtro():
    print("Escolha um filtro:\n")

    chaves = list(FILTROS.keys())

    for i, nome in enumerate(chaves):
        print(f"{i} -> {nome}")

    print("-1 para sair")

    while True:
        try:
            escolha = int(input("\nDigite o número do filtro: "))
            if escolha == -1: 
               break
            global KEY
            KEY = chaves[escolha]
            return FILTROS[chaves[escolha]]  # retorna a regex
        except:
            print("Entrada inválida")
    print("saindo...")
    exit()

def gerarJson(data,fileName):
    with open(fileName, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        print("[OK] Arquivo " +fileName + " gerado")

def gerarHtml(data,fileName):
    text = "<table>\n"
    count = 0
    for e in data:
       count += 1 
       path = e["path"]
       assunto = e["assunto"]
       text += f"<tr><td>{count}</td><td><a href='{ROOT+path}' target='_blank'>{path}</a></td><td>{assunto}</td></tr>\n"
    text += "</table>\n"
    with open(fileName, "w", encoding="utf-8") as f:
        f.write(text)
        print("[OK] Arquivo " +fileName + " gerado")

def verOpcoes():
    print("1 -> listar")
    print("2 -> gerar json")
    print("3 -> gerar pdf")
    print("4 -> gerar html")
    print("5 -> gerar tudo")
    print("6 -> ver opcoes")
    print("7 -> sair")


def main():
    with open(INPUT, encoding="utf-8") as f:
        dados = json.load(f)

    filtro = escolher_filtro()

    filtrados = []

    for item in dados:
        ultima = item.get("ultima_revisao")

        if not ultima:
            continue

        path = ultima.get("path", "")

        if verificar(path, filtro):
            filtrados.append({
                "id": item["id"],
                "path": path,
                "assunto": ultima.get("assunto", "")
            })

    print(f"\n[INFO] {len(filtrados)} itens encontrados")
    paths = [ ROOT + item["path"] for item in filtrados]

    verOpcoes()
    while True:
        escolha = int(input("\nDigite o número: "))
        if escolha == 1: 
           print("\n".join(paths))
           print(f"\n[Size] {len(filtrados)}")
        elif escolha == 2:
            gerarJson(filtrados,KEY+".json")
            print("escolhido " + str(escolha))
        elif escolha == 3:
            pdf.criarPdf(paths,KEY + ".pdf") 
            print("escolhido " + str(escolha))
        elif escolha == 4:
            gerarHtml(filtrados,KEY+"html")
            print("escolhido " + str(escolha))
        elif escolha == 5:
            gerarHtml(filtrados,KEY+".html")
            gerarJson(filtrados,KEY+".json")
            pdf.criarPdf(paths,KEY + ".pdf") 
            break
        elif escolha == 6:
            verOpcoes()
            print("escolhido " + str(escolha))
        elif escolha > 6:
            break
    print("saindo...")
    exit()

if __name__ == "__main__":
    main()
