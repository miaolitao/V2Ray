#!/bin/bash
# V2Ray 节点聚合系统安装脚本

set -e

echo "=========================================="
echo "V2Ray 节点聚合系统安装脚本"
echo "=========================================="
echo ""

# 检查 Python 版本
echo "检查 Python 版本..."
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python 3"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Python 版本: $PYTHON_VERSION"

# 检查并安装 uv
echo ""
echo "检查 uv 包管理器..."
if ! command -v uv &> /dev/null; then
    echo "uv 未安装，正在安装..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # 添加到当前 shell
    export PATH="$HOME/.cargo/bin:$PATH"
    
    if ! command -v uv &> /dev/null; then
        echo "错误: uv 安装失败"
        echo "请手动安装: curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
    
    echo "✓ uv 安装成功"
else
    echo "✓ uv 已安装"
fi

# 创建必要的目录
echo ""
echo "创建项目目录..."
mkdir -p config
mkdir -p logs
mkdir -p output
mkdir -p tests
echo "✓ 目录创建完成"

# 安装依赖
echo ""
echo "安装 Python 依赖..."
uv pip install -e .
echo "✓ 依赖安装完成"

# 安装开发依赖（可选）
read -p "是否安装开发依赖（用于测试）？ [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "安装开发依赖..."
    uv pip install -e ".[dev]"
    echo "✓ 开发依赖安装完成"
fi

# 检查配置文件
echo ""
echo "检查配置文件..."
if [ ! -f "config/sources.yaml" ]; then
    echo "警告: 未找到 config/sources.yaml"
fi
if [ ! -f "config/settings.yaml" ]; then
    echo "警告: 未找到 config/settings.yaml"
fi

echo ""
echo "=========================================="
echo "✓ 安装完成！"
echo "=========================================="
echo ""
echo "使用方法:"
echo "  1. 运行完整更新: make update"
echo "  2. 快速更新（跳过测速）: make update-quick"
echo "  3. 查看帮助: make help"
echo ""
echo "或者直接运行:"
echo "  python main.py"
echo ""

