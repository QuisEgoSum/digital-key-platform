#!/bin/bash
if [[ "$OSTYPE" != "msys"* && "$OSTYPE" != "win32" && "$OSTYPE" != "cygwin" ]]; then
  set -euo pipefail
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
export PYTHONPATH="$ROOT_DIR/src"

echo $SCRIPT_DIR
echo $ROOT_DIR

"$ROOT_DIR/src/scripts/generate_env_list_md.py"

git add "$ROOT_DIR/docs/config/ENV_LIST.md"