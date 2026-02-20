#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

OUT_DIR="${PROJECT_ROOT}/local/pdf"
STYLE="${PROJECT_ROOT}/resources/pdf_style.css"
BODY_CLASS="markdown-body"

mkdir -p "$OUT_DIR"

if [[ ! -f "$STYLE" ]]; then
  echo "Style not found: $STYLE" >&2
  echo "pwd=$(pwd)" >&2
  echo "SCRIPT_DIR=$SCRIPT_DIR" >&2
  echo "PROJECT_ROOT=$PROJECT_ROOT" >&2
  exit 3
fi

while IFS= read -r -d '' input; do
  rel="${input#"$PROJECT_ROOT"/}"
  stem="${rel%.md}"
  flat="${stem//\//_}"
  flat="${flat//-/_}"
  flat="${flat^^}"
  output="${OUT_DIR}/${flat}.pdf"

  echo "$rel -> ${output#"$PROJECT_ROOT"/}"

  md-to-pdf --stylesheet "$STYLE" --body-class "$BODY_CLASS" < "$input" > "$output"
done < <(
  find "$PROJECT_ROOT" \
    -type d \( -name .git -o -name node_modules -o -name .venv \) -prune -o \
    -path "$PROJECT_ROOT/local" -prune -o \
    -type f -name '*.md' -print0
)

echo "Done: $OUT_DIR"
