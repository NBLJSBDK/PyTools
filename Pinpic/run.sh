#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")"

if [[ -x .venv/bin/python ]]; then
  exec ./.venv/bin/python ./pinpic.py "$@"
fi

echo 'Pinpic 尚未安装依赖，请先运行：' >&2
echo '  ./install.sh' >&2
exit 1
