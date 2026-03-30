from pypdf import PdfReader, PdfWriter

def criarPdf(paths ,fileName):
    merge = PdfWriter()
    for p in paths:
        reader = PdfReader(p)
        for page in reader.pages:
            merge.add_page(page)
    with open(fileName,"wb") as f:
        merge.write(f)
        print(f"[OK] Arquivo {fileName} Criado.")


