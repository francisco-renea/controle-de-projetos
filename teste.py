import re

def extrair_info(path):
    # pega só o nome do arquivo
    nome = path.split("/")[-1]

    # regex:
    # (.*\.R)  -> tudo até ".R"
    # ([^.]*)  -> revisão (até o próximo ponto)
    # \.(.+)   -> extensão
    match = re.match(r"(.*\.R)([^.]*)\.(.+)", nome)

    if not match:
        return None

    return {
        "id": match.group(1),          # até .R
        "revisao": match.group(2),     # ex: 0b
        "extensao": match.group(3)     # ex: docx
    }


path = "CANHEDO/FASE 01/01-Projeto Geométrico/PROJETOS/MD-SPM00021D-114.116-825-F09_001.R0b.docx"

print(extrair_info(path))
