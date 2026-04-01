#!bash sh
FILE="$HOME/Downloads/OneDrive_2026-04-01.zip"
unzip -Z1 $FILE | grep "^PROJETOS REVISADOS - COMPLEXO DO ALTO TIETÊ/" | while read file; do
    destino="$HOME/Documents/CONSOLIDADO/CANHEDO/${file#PROJETOS REVISADOS - COMPLEXO DO ALTO TIETÊ/}"

    if [ ! -f "$destino" ]; then
        mkdir -p "$(dirname "$destino")"
        unzip -p $FILE "$file" > "$destino"
    fi
done

