#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")"

if [[ ! -x venv/bin/python ]]; then
  echo '尚未创建虚拟环境，请先运行 ./install.sh' >&2
  exit 1
fi

export QT_IM_MODULE=fcitx
exec ./venv/bin/python ./typing_practice.py >> /tmp/typing-practice.log 2>&1
