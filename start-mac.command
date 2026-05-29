#!/bin/zsh
set -euo pipefail

# macOS 一键启动脚本：双击本文件即可启动前后端服务并打开浏览器。
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
LOG_DIR="$ROOT_DIR/.logs"
API_PORT="${API_PORT:-8000}"
UI_PORT="${UI_PORT:-3000}"
API_URL="http://127.0.0.1:${API_PORT}"
UI_URL="http://127.0.0.1:${UI_PORT}"

mkdir -p "$LOG_DIR"

info() {
  printf "\033[1;36m[DWCA]\033[0m %s\n" "$1"
}

fail() {
  printf "\033[1;31m[DWCA]\033[0m %s\n" "$1" >&2
  printf "\n按任意键关闭窗口..."
  read -k 1
  exit 1
}

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

port_is_busy() {
  lsof -nP -iTCP:"$1" -sTCP:LISTEN >/dev/null 2>&1
}

wait_for_url() {
  local url="$1"
  local name="$2"
  local tries=60
  for _ in $(seq 1 "$tries"); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      info "$name 已就绪：$url"
      return 0
    fi
    sleep 1
  done
  return 1
}

cleanup() {
  info "正在停止本次脚本启动的服务..."
  if [[ -n "${BACKEND_PID:-}" ]]; then kill "$BACKEND_PID" >/dev/null 2>&1 || true; fi
  if [[ -n "${FRONTEND_PID:-}" ]]; then kill "$FRONTEND_PID" >/dev/null 2>&1 || true; fi
}

trap cleanup INT TERM EXIT

cd "$ROOT_DIR"
info "项目目录：$ROOT_DIR"

command_exists python3 || fail "未找到 python3。请先安装 Python 3.11+。"
command_exists npm || fail "未找到 npm。请先安装 Node.js 20+。"
command_exists curl || fail "未找到 curl。"

if port_is_busy "$API_PORT"; then
  fail "端口 ${API_PORT} 已被占用。可先关闭占用进程，或用 API_PORT=8001 ./start-mac.command 指定新端口。"
fi

if port_is_busy "$UI_PORT"; then
  fail "端口 ${UI_PORT} 已被占用。可先关闭占用进程，或用 UI_PORT=3001 ./start-mac.command 指定新端口。"
fi

info "准备后端 Python 环境..."
cd "$BACKEND_DIR"
if [[ ! -d ".venv" ]]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
python -m pip install --upgrade pip >/dev/null
pip install -r requirements.txt

info "准备前端 Node 环境..."
cd "$FRONTEND_DIR"
if [[ ! -d "node_modules" ]]; then
  npm install
else
  npm install --silent
fi

info "启动 FastAPI 后端..."
cd "$BACKEND_DIR"
source .venv/bin/activate
# 一键 demo 默认使用轻量 hash embedding，避免首次启动/分析下载 HuggingFace 模型卡住。
EMBEDDING_PROVIDER="${EMBEDDING_PROVIDER:-hash}" python -m uvicorn app.main:app --host 127.0.0.1 --port "$API_PORT" > "$LOG_DIR/backend.log" 2>&1 &
BACKEND_PID=$!

wait_for_url "$API_URL/health" "后端" || fail "后端启动超时。请查看日志：$LOG_DIR/backend.log"

info "写入 demo 数据..."
curl -fsS -X POST "$API_URL/demo/seed" >/dev/null || info "demo seed 未完成，可稍后在 Swagger 手动执行。"

info "启动 Next.js 前端..."
cd "$FRONTEND_DIR"
NEXT_PUBLIC_API_BASE_URL="$API_URL" npm run dev -- --hostname 127.0.0.1 --port "$UI_PORT" > "$LOG_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!

wait_for_url "$UI_URL" "前端" || fail "前端启动超时。请查看日志：$LOG_DIR/frontend.log"

info "打开浏览器..."
open "$UI_URL"

cat <<EOF

Delegate Writing Consistency Analyzer 已启动。

前端：$UI_URL
后端：$API_URL
Swagger：$API_URL/docs

日志：
- $LOG_DIR/backend.log
- $LOG_DIR/frontend.log

保持此窗口打开即可持续运行服务。
按 Ctrl+C 可停止本次启动的前后端进程。

EOF

while true; do
  sleep 3600
done
