.PHONY: help install update test clean lint format

# 默认目标
help:
	@echo "V2Ray 节点聚合系统 - Makefile 命令"
	@echo ""
	@echo "可用命令:"
	@echo "  make install    - 安装项目依赖（使用 uv）"
	@echo "  make update     - 运行节点更新"
	@echo "  make update-quick - 快速更新（跳过测速）"
	@echo "  make test       - 运行测试"
	@echo "  make clean      - 清理临时文件和输出"
	@echo "  make lint       - 代码检查"
	@echo "  make format     - 代码格式化"
	@echo ""

# 安装依赖（使用 uv）
install:
	@echo "安装依赖（使用 uv）..."
	@if command -v uv >/dev/null 2>&1; then \
		uv pip install -e .; \
	else \
		echo "错误: 未找到 uv，请先安装 uv"; \
		echo "安装方法: curl -LsSf https://astral.sh/uv/install.sh | sh"; \
		exit 1; \
	fi
	@echo "创建必要的目录..."
	@mkdir -p logs output
	@echo "安装完成!"

# 更新节点（完整流程）
update:
	@echo "开始更新节点（完整流程）..."
	python main.py

# 快速更新（跳过测速）
update-quick:
	@echo "开始快速更新（跳过测速）..."
	python main.py --skip-test

# 仅生成指定格式
update-base64:
	python main.py --format base64

update-clash:
	python main.py --format clash

update-v2ray:
	python main.py --format v2ray

update-surge:
	python main.py --format surge

update-quantumult:
	python main.py --format quantumult

# 运行测试
test:
	@echo "运行测试..."
	@if command -v uv >/dev/null 2>&1; then \
		uv pip install -e ".[dev]"; \
		pytest tests/ -v; \
	else \
		pytest tests/ -v; \
	fi

# 清理文件
clean:
	@echo "清理临时文件..."
	rm -rf __pycache__ .pytest_cache .coverage
	rm -rf src/__pycache__ utils/__pycache__
	rm -rf tests/__pycache__
	rm -rf build dist *.egg-info
	@echo "清理输出文件..."
	rm -rf output/*
	rm -rf logs/*.log
	@echo "清理完成!"

# 代码检查
lint:
	@echo "代码检查..."
	@if command -v ruff >/dev/null 2>&1; then \
		ruff check src/ utils/ tests/; \
	else \
		echo "未安装 ruff，跳过检查"; \
	fi

# 代码格式化
format:
	@echo "代码格式化..."
	@if command -v black >/dev/null 2>&1; then \
		black src/ utils/ tests/; \
	else \
		echo "未安装 black，跳过格式化"; \
	fi
	@if command -v ruff >/dev/null 2>&1; then \
		ruff check --fix src/ utils/ tests/; \
	fi

# 显示统计信息
stats:
	@if [ -f output/stats.json ]; then \
		cat output/stats.json; \
	else \
		echo "未找到统计文件，请先运行 make update"; \
	fi

# 查看日志
logs:
	@if [ -d logs ] && [ -n "$$(ls -A logs)" ]; then \
		ls -lt logs/ | head -5; \
	else \
		echo "没有日志文件"; \
	fi

