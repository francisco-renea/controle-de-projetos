import os
import json
import zipfile
from pathlib import Path
from datetime import datetime

DOWNLOADS = Path.home() / "Downloads"
DEST_CANHEDO = Path.home() / "Documents/CONSOLIDADO/CANHEDO"
DEST_ENESCIL = Path.home() / "Documents/CONSOLIDADO/ENESCIL"
CONTROL_FILE = Path.home() / ".zip_processados.json"

PASTA_CANHEDO = "PROJETOS REVISADOS - COMPLEXO DO ALTO TIETÊ/"
PASTA_ENESCIL = "REVISÃO DE PROJETOS - ENESCIL/"


def carregar_controle():
    if CONTROL_FILE.exists():
        return json.loads(CONTROL_FILE.read_text())
    return {}


def salvar_controle(data):
    CONTROL_FILE.write_text(json.dumps(data, indent=2))


def get_ultimos_zips(n=2):
    arquivos = list(DOWNLOADS.glob("*.zip"))
    arquivos.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return arquivos[:n]


def ja_processado(zip_path, controle):
    key = str(zip_path)
    mtime = zip_path.stat().st_mtime
    return key in controle and controle[key] == mtime


def registrar(zip_path, controle):
    controle[str(zip_path)] = zip_path.stat().st_mtime


def extrair_prefixo(zip_path, prefixo, destino):
    with zipfile.ZipFile(zip_path) as z:
        for member in z.namelist():
            if member.startswith(prefixo) and not member.endswith("/"):
                relative_path = member[len(prefixo):]
                target_path = destino / relative_path

                target_path.parent.mkdir(parents=True, exist_ok=True)

                with z.open(member) as source, open(target_path, "wb") as target:
                    target.write(source.read())


def processar_zip(zip_path, controle):
    with zipfile.ZipFile(zip_path) as z:
        nomes = z.namelist()

        if any(n.startswith(PASTA_CANHEDO) for n in nomes):
            extrair_prefixo(zip_path, PASTA_CANHEDO, DEST_CANHEDO)
            registrar(zip_path, controle)
            print(f"[OK] CANHEDO: {zip_path}")
            return

        if any(n.startswith(PASTA_ENESCIL) for n in nomes):
            extrair_prefixo(zip_path, PASTA_ENESCIL, DEST_ENESCIL)
            registrar(zip_path, controle)
            print(f"[OK] ENESCIL: {zip_path}")
            return

        print(f"[SKIP] Não reconhecido: {zip_path}")


def main():
    controle = carregar_controle()
    zips = get_ultimos_zips()

    for zip_path in zips:
        if ja_processado(zip_path, controle):
            print(f"[SKIP] Já processado: {zip_path}")
            continue

        processar_zip(zip_path, controle)

    salvar_controle(controle)

    # chama outro programa
    os.system("python outro_programa.py")


if __name__ == "__main__":
    main()
