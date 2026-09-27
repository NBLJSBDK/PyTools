#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")"

if ! command -v python3 >/dev/null 2>&1; then
  echo '错误：找不到 python3。' >&2
  exit 1
fi

echo 'Python:' "$(python3 -c 'import sys; print(sys.version.split()[0])')"

# 上一次失败的 venv 不应影响重试。
rm -rf venv

if ! python3 -m venv venv; then
  rm -rf venv
  echo >&2
  echo '创建 Python 虚拟环境失败。' >&2
  if [[ -r /etc/os-release ]]; then
    # shellcheck disable=SC1091
    . /etc/os-release
    case "${ID:-}" in
      debian|ubuntu|linuxmint)
        echo 'Debian/Ubuntu 可先安装：sudo apt install python3-venv' >&2
        ;;
      arch|manjaro|endeavouros)
        echo 'Arch 系若 Python 安装不完整：sudo pacman -S python' >&2
        ;;
    esac
  fi
  exit 2
fi

./venv/bin/python -m pip install --upgrade pip
./venv/bin/python -m pip install 'PyQt5==5.15.10'

# pip 版 PyQt5 只搜索 venv 内的 Qt 插件目录，把系统 fcitx5 输入法插件链进来。
PLUGIN_DIRS=(
  /usr/lib/qt/plugins/platforminputcontexts
  /usr/lib/x86_64-linux-gnu/qt5/plugins/platforminputcontexts
  /usr/lib64/qt5/plugins/platforminputcontexts
)
LINKED=0
for dir in "${PLUGIN_DIRS[@]}"; do
  src="$dir/libfcitx5platforminputcontextplugin.so"
  if [[ -f "$src" ]]; then
    for dest in venv/lib/python*/site-packages/PyQt5/Qt5/plugins/platforminputcontexts; do
      ln -sf "$src" "$dest/"
    done
    LINKED=1
    echo "已链接 fcitx5 输入法插件：$src"
    break
  fi
done
if [[ "$LINKED" -eq 0 ]]; then
  echo '提示：未找到 fcitx5 Qt5 插件，无法输入中文时请安装 fcitx5-qt。' >&2
fi

if command -v gst-inspect-1.0 >/dev/null 2>&1 && ! gst-inspect-1.0 wavparse >/dev/null 2>&1; then
  echo '提示：缺少 GStreamer 解码器，音效无法播放，可安装 gst-plugins-good gst-libav。' >&2
fi

echo
echo '安装完成。'
echo '运行：./run.sh'
