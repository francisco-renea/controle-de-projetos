import pandas as pd

arquivo_excel = "assuntoEnescil.xlsx"

# lê todas as sheets
sheets = pd.read_excel(arquivo_excel, sheet_name=None)

# concatena
df_final = pd.concat(sheets.values(), ignore_index=True)

# salva com separador ;
df_final.to_csv("enescil.csv", index=False, sep=";", encoding="utf-8-sig")

print("Arquivo enescil.csv criado com separador ';'.")
