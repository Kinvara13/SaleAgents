#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# 一键启动脚本：启动 SaleAgents V2 后端与前端服务
# 使用方式:
#   ./start.sh        # 开发模式 (Vite dev + HMR)
#   ./start.sh --prod # 生产模式 (build + preview)
# -----------------------------------------------------------------------------

# 设置严格模式：遇到错误即退出
set -e

# 获取脚本所在目录的绝对路径，确保在任何地方执行都正确
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${PROJECT_ROOT}/logs"
PID_FILE="${PROJECT_ROOT}/.run.pid"

# 判断启动模式
MODE="dev"
if [ "$1" == "--prod" ]; then
    MODE="prod"
    echo "========================================================="
    echo "🚀 正在以生产模式启动 SaleAgents V2 项目..."
    echo "========================================================="
else
    echo "========================================================="
    echo "🚀 正在以开发模式启动 SaleAgents V2 项目..."
    echo "========================================================="
fi

# 创建日志目录
mkdir -p "${LOG_DIR}"

# 检查是否已经在运行
if [ -f "${PID_FILE}" ]; then
    echo "⚠️ 发现已存在的进程锁文件 (${PID_FILE})。"
    echo "请先执行 ./stop.sh 停止服务，或手动删除该文件。"
    exit 1
fi

# 记录进程 ID
> "${PID_FILE}"

# ---------------------------------------------------------
# 1. 启动后端服务 V2 (FastAPI / Uvicorn)
# ---------------------------------------------------------
echo "[1/2] 正在启动后端服务 V2 (端口: 8000)..."
cd "${PROJECT_ROOT}/backend-v2"

# 检查并激活虚拟环境
if [ ! -d ".venv" ]; then
    echo "  > 未找到虚拟环境 (.venv)，正在创建..."
    # 使用 Python 3.11（如果可用）
    if command -v python3.11 &> /dev/null; then
        python3.11 -m venv .venv
    else
        python3 -m venv .venv
    fi
    source .venv/bin/activate
    echo "  > 正在安装依赖..."
    pip install --upgrade pip setuptools wheel -q
    pip install -r requirements.txt uvicorn -q
else
    source .venv/bin/activate
fi

# 确保环境变量使用 SQLite
export DATABASE_URL_OVERRIDE="sqlite:///./sale_agents_v2.db"

# 根据模式设置 CORS 允许的前端地址
if [ "$MODE" == "prod" ]; then
    export FRONTEND_ORIGINS="http://47.85.54.50:8081"
else
    export FRONTEND_ORIGINS="http://localhost:8081,http://127.0.0.1:8081"
fi

# 启动后端 (后台运行)
nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > "${LOG_DIR}/backend-v2.log" 2>&1 &
BACKEND_PID=$!
echo "${BACKEND_PID}" >> "${PID_FILE}"
echo "  ✓ 后端 V2 已启动 (PID: ${BACKEND_PID})，日志: logs/backend-v2.log"
echo "     CORS 允许来源: ${FRONTEND_ORIGINS}"

# ---------------------------------------------------------
# 2. 启动前端服务 V2 (Vue / Vite)
# ---------------------------------------------------------
cd "${PROJECT_ROOT}/frontend-v2"

# 检查 node_modules
if [ ! -d "node_modules" ]; then
    echo "  > 未找到 node_modules，正在安装前端依赖..."
    npm install
fi

if [ "$MODE" == "prod" ]; then
    echo "[2/2] 正在构建前端生产包 (端口: 8081)..."
    npm run build
    echo "  > 启动预览服务器..."
    nohup npm run preview -- --host --port 8081 > "${LOG_DIR}/frontend-v2.log" 2>&1 &
    FRONTEND_PID=$!
    echo "${FRONTEND_PID}" >> "${PID_FILE}"
    echo "  ✓ 前端 V2 已启动 (PID: ${FRONTEND_PID})，日志: logs/frontend-v2.log"
else
    echo "[2/2] 正在启动前端开发服务器 (端口: 8081, HMR 已启用)..."
    nohup npm run dev > "${LOG_DIR}/frontend-v2.log" 2>&1 &
    FRONTEND_PID=$!
    echo "${FRONTEND_PID}" >> "${PID_FILE}"
    echo "  ✓ 前端 V2 已启动 (PID: ${FRONTEND_PID})，日志: logs/frontend-v2.log"
    echo "     💡 代码修改会自动热更新，无需手动 build"
fi

# ---------------------------------------------------------
echo "========================================================="
echo "✅ 所有服务启动成功！"
if [ "$MODE" == "prod" ]; then
    echo "🌐 前端访问地址: http://47.85.54.50:8081"
else
    echo "🌐 前端访问地址: http://localhost:8081"
fi
echo "🔌 后端 API 地址: http://localhost:8000"
echo "🛑 停止服务请执行: ./stop.sh"
echo "========================================================="
