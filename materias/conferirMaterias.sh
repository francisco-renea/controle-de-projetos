#!/bin/bash
# Define que o script será executado usando o interpretador bash
export LANG=pt_BR.UTF-8
export LC_ALL=pt_BR.UTF-8

set -e
# Faz o script parar imediatamente se qualquer comando der erro

# ===== CONFIG =====
MATERIAS_FILE="materias.txt"
# Arquivo que contém a lista de matérias (uma por linha)

# Pasta onde os arquivos de saída serão salvos

DATA=$(date +%Y-%m-%d)
OUTPUT_DIR="relatorios_$DATA"
# Gera timestamp atual (ano-mês-dia_hora-minuto-segundo) para versionar os arquivos

mkdir -p "$OUTPUT_DIR"
# Cria a pasta de saída se ela não existir (-p evita erro se já existir)

# ===== 1. Snapshot do git =====
SNAPSHOT="$OUTPUT_DIR/git_ls_files.txt"
# Define o nome do arquivo que vai armazenar o snapshot do git

git -C "$HOME/Documents/CONSOLIDADO/" ls-files > "$SNAPSHOT"
# Lista todos os arquivos versionados no git e salva no snapshot

echo "[OK] Snapshot criado: $SNAPSHOT"
# Mostra mensagem de confirmação

# ===== 2. Total de arquivos =====
TOTAL=$(wc -l < "$SNAPSHOT")
# Conta quantas linhas (arquivos) existem no snapshot

echo "[INFO] Total git ls-files: $TOTAL"
# Exibe o total de arquivos

# ===== 3. Separar por matéria =====
SOMA=0
# Inicializa variável que vai acumular a soma dos arquivos por matéria

while IFS= read -r materia; do
# Lê o arquivo materias.txt linha por linha
# IFS= evita cortar espaços
# -r evita interpretar caracteres especiais (ex: \)

  [ -z "$materia" ] && continue
  # Se a linha estiver vazia, pula para a próxima

  OUT_FILE="$OUTPUT_DIR/${materia//[^[:alnum:] _-]/_}.txt"
  # Define nome do arquivo de saída da matéria
  # Substitui "/" por "_" para evitar problema em nome de arquivo

  grep -a -E "$materia" "$SNAPSHOT" > "$OUT_FILE" || true
  # Filtra no snapshot os arquivos que contêm o nome da matéria
  # Salva no arquivo correspondente
  # "|| true" evita o script parar caso grep não encontre nada

  COUNT=$(wc -l < "$OUT_FILE")
  # Conta quantos arquivos foram encontrados para essa matéria

  echo "[INFO] $materia -> $COUNT arquivos"
  # Mostra quantidade por matéria

  SOMA=$((SOMA + COUNT))
  # Soma ao total acumulado

done < "$MATERIAS_FILE"
# Indica que o loop vai ler o arquivo materias.txt

# ===== 4. Verificação =====
echo "----------------------------------"
# Separador visual

echo "[INFO] Soma das matérias: $SOMA"
# Mostra soma total dos arquivos classificados

echo "[INFO] Total git:         $TOTAL"
# Mostra total real do git

if [ "$SOMA" -ne "$TOTAL" ]; then
# Compara se a soma das matérias é diferente do total do git

  echo "[ALERTA] Divergência detectada!"
  # Se for diferente, alerta erro

  echo "Possível matéria nova ou filtro incorreto."
  # Explica possível causa

else
  echo "[OK] Tudo consistente."
  # Se for igual, está tudo certo
fi
