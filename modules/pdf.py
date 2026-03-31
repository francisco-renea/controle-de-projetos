from pypdf import PdfReader, PdfWriter

def criarPdf(paths ,fileName):
    merge = PdfWriter()

    print("arquivos que montarao o pdf:")
    validos = []
    for p in paths:
        if not ".pdf" in p.lower():
            continue
        if "rt-" in p.lower():
            continue
        if "mc-" in p.lower():
            continue
        if "md-" in p.lower():
            continue
        if "final." in p.lower():
            continue
        validos.append(p)
        print(p)
    print("size=" + str(len(validos)))

    entrada = input("Tem certeza que quer montar o PDF? <y/n> ")
    if entrada.lower() == "n":
        return

#txt do que vai ser imprimiido
    text = ""
    for p in validos:
        text += p + "\n"
    with open(fileName+".txt","w") as f:
        f.write(text)
    return

    for p in validos:
        reader = PdfReader(p)
        for page in reader.pages:
            merge.add_page(page)
    with open(fileName,"wb") as f:
        merge.write(f)
        print(f"[OK] Arquivo {fileName} Criado.")

