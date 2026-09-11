#!/usr/bin/env bash
cd "$(dirname "$(readlink -f "$0")")"
export QT_IM_MODULE=fcitx
exec ./venv/bin/python ./typing_practice.py >> /tmp/typing-practice.log 2>&1
