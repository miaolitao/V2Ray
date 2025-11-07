# V2Ray 节点聚合系统

![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/miaolitao/V2Ray/update-nodes.yml?style=flat-square)
![Python Version](https://img.shields.io/badge/python-3.9+-blue?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

一个强大的 V2Ray 免费节点聚合系统，支持多源爬取、智能去重、速度测试和多格式输出。

## ✨ 主要特性

- 🚀 **多源收集**：支持订阅链接、GitHub 仓库等多种节点源
- 🔄 **智能去重**：基于配置哈希和服务器地址的双重去重机制
- ⚡ **速度测试**：异步并发测速，筛选高质量节点
- 📦 **多格式输出**：支持 Base64、Clash、V2Ray、Surge、Quantumult X 等格式
- 🤖 **自动更新**：GitHub Actions 定时自动更新（每 6 小时）
- 🛠️ **本地运行**：支持命令行参数，灵活配置
- 🌐 **全协议支持**：SS、SSR、VMess、Trojan、VLESS 五种协议

## 📱 订阅链接

> **注意**：订阅链接通过 GitHub Pages 托管，每 6 小时自动更新一次。

### 🌐 在线订阅页面

访问订阅页面查看所有可用格式：

**🔗 https://miaolitao.github.io/V2Ray/**

### 📜 历史版本功能

✨ **新功能**：现在支持查看历史版本，保留最近 10 次更新记录！

- 🕐 **自动保存**：每次更新自动创建时间戳目录
- 📊 **版本列表**：主页显示历史版本，按时间倒序排列
- 🔍 **版本详情**：点击任意历史版本查看详情和订阅链接
- 🗑️ **自动清理**：自动删除超过 10 次的旧版本
- 🔗 **独立链接**：每个历史版本都有独立的订阅链接

**访问方式**：
- 主页查看历史列表：https://miaolitao.github.io/V2Ray/
- 历史版本详情：https://miaolitao.github.io/V2Ray/history.html?v=2025-11-07_18-40-00
- 历史版本订阅：https://miaolitao.github.io/V2Ray/history/2025-11-07_18-40-00/nodes.txt

### 📋 直接订阅链接

#### Base64 通用订阅
```
https://miaolitao.github.io/V2Ray/nodes.txt
```
适用于：Shadowrocket、V2RayNG、Qv2ray 等

#### Clash 订阅
```
https://miaolitao.github.io/V2Ray/clash.yaml
```
适用于：Clash for Windows、Clash for Android、ClashX 等

#### Surge 订阅
```
https://miaolitao.github.io/V2Ray/surge.conf
```
适用于：Surge iOS、Surge Mac

#### Quantumult X 订阅
```
https://miaolitao.github.io/V2Ray/quantumult.conf
```
适用于：Quantumult X

### 📊 节点统计

```
https://miaolitao.github.io/V2Ray/stats.json
```

### ⚠️ 免责声明

本项目仅供学习和技术研究使用。节点来源于互联网公开渠道，不保证可用性、稳定性和安全性。请勿用于非法用途，使用本项目所产生的一切后果由使用者自行承担。

## 📋 系统要求

- Python 3.9 或更高版本
- [uv](https://github.com/astral-sh/uv) 包管理器（推荐）
- 操作系统：Linux / macOS / Windows

## 🚀 快速开始

### 安装

#### 方法 1: 使用安装脚本（推荐）

```bash
# 克隆仓库
git clone https://github.com/miaolitao/V2Ray.git
cd V2Ray

# 运行安装脚本
bash scripts/install.sh
```

#### 方法 2: 手动安装

```bash
# 安装 uv（如果未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装依赖
uv pip install -e .

# 创建必要的目录
mkdir -p logs output
```

### 使用

#### 使用 Makefile（推荐）

```bash
# 切换虚拟环境
source .venv/bin/activate

# 查看所有命令
make help

# 完整更新（收集 + 测速 + 生成所有格式）
make update

# 快速更新（跳过测速）
make update-quick

# 仅生成指定格式
make update-clash
make update-base64
```

#### 直接运行

```bash
# 完整更新
python main.py

# 跳过测速
python main.py --skip-test

# 指定输出格式
python main.py --format clash

# 自定义输出目录
python main.py --output-dir custom_output

# 限制节点数量
python main.py --max-nodes 100

# 调试模式
python main.py --log-level DEBUG
```

### 命令行参数

| 参数 | 说明 | 默认值 |
|-----|------|--------|
| `--skip-test` | 跳过测速步骤 | False |
| `--source` | 指定节点源名称 | 所有源 |
| `--format` | 输出格式（all/base64/clash/v2ray/surge/quantumult） | all |
| `--output-dir` | 输出目录 | output |
| `--log-level` | 日志级别（DEBUG/INFO/WARNING/ERROR） | INFO |
| `--max-nodes` | 最大节点数量 | 200 |

## 📁 项目结构

```
V2Ray/
├── .github/
│   └── workflows/          # GitHub Actions 工作流
│       ├── update-nodes.yml # 自动更新节点
│       └── test.yml        # 自动测试
├── config/                 # 配置文件
│   ├── sources.yaml        # 节点源配置
│   ├── settings.yaml       # 系统设置
│   └── clash_template.yaml # Clash 模板
├── src/                    # 核心代码
│   ├── collector.py        # 节点收集器
│   ├── parser.py           # 节点解析器
│   ├── deduplicator.py     # 去重模块
│   ├── formatter.py        # 格式转换器
│   ├── speed_tester.py     # 测速模块
│   └── config_manager.py   # 配置管理
├── utils/                  # 工具模块
│   ├── logger.py           # 日志工具
│   ├── network.py          # 网络工具
│   └── validator.py        # 验证工具
├── tests/                  # 测试文件
├── scripts/                # 脚本文件
│   └── install.sh          # 安装脚本
├── output/                 # 输出文件（按时间戳分类）
│   ├── 2025-11-06_18-01-46/  # 时间戳目录（yyyy-MM-dd_HH-mm-ss）
│   │   ├── nodes.txt       # Base64 格式
│   │   ├── clash.yaml      # Clash 配置
│   │   ├── v2ray.json      # V2Ray 配置
│   │   ├── surge.conf      # Surge 配置
│   │   ├── quantumult.conf # Quantumult 配置
│   │   └── stats.json      # 统计信息
│   └── latest -> 2025-11-06_18-01-46  # 指向最新结果的符号链接
├── logs/                   # 日志目录
├── main.py                 # 主程序
├── Makefile                # Make 命令
├── pyproject.toml          # 项目配置（uv）
└── README.md               # 项目说明
```

## ⚙️ 配置说明

### 节点源配置（config/sources.yaml）

```yaml
subscription_sources:
  - name: "源名称"
    url: "订阅链接"
    enabled: true
    type: "base64"  # 或 "clash"

github_sources:
  - name: "GitHub源"
    repo: "用户名/仓库名"
    file: "文件路径"
    enabled: true
```

### 系统设置（config/settings.yaml）

```yaml
# 测速配置
speed_test:
  enabled: true
  timeout: 15
  min_speed: 1.0      # 最低速度要求（MB/s）
  max_latency: 1000   # 最大延迟（ms）
  concurrent_tests: 50 # 并发测速数量

# 输出配置
output:
  max_nodes: 200
  sort_by: "speed"    # 排序方式：speed, latency
  formats:
    - base64
    - clash
    - v2ray
```

## 🤖 GitHub Actions 自动化

项目配置了 GitHub Actions 工作流，可实现：

- ⏰ **定时更新**：每 6 小时自动运行一次
- 🔘 **手动触发**：在 Actions 页面手动触发更新
- 📝 **自动提交**：更新后自动提交到仓库
- 📦 **产物上传**：保存输出文件和日志

### 启用 GitHub Actions

1. Fork 本仓库到你的 GitHub 账号
2. 进入仓库设置 → Actions → General
3. 启用 "Read and write permissions"
4. GitHub Actions 将自动运行

### 手动触发更新

1. 进入仓库的 Actions 页面
2. 选择 "更新节点" 工作流
3. 点击 "Run workflow"
4. 选择是否跳过测速和输出格式
5. 点击 "Run workflow" 执行

## 📊 输出格式说明

### Base64 格式（nodes.txt）

通用订阅格式，兼容大多数客户端：

```
ss://base64encodedstring#节点1
vmess://base64encodedstring#节点2
...
```

### Clash 格式（clash.yaml）

完整的 Clash 配置文件，包含节点、规则和代理组：

```yaml
proxies:
  - name: 节点1
    type: ss
    server: 1.1.1.1
    port: 443
    ...
```

### V2Ray 格式（v2ray.json）

标准的 V2Ray JSON 配置：

```json
{
  "outbounds": [
    {
      "protocol": "shadowsocks",
      "settings": {...}
    }
  ]
}
```

### 其他格式

- **Surge**（surge.conf）：适用于 Surge iOS/macOS 客户端
- **Quantumult X**（quantumult.conf）：适用于 Quantumult X 客户端

## 🧪 测试

```bash
# 运行所有测试
make test

# 或使用 pytest
pytest tests/ -v

# 测试覆盖率
pytest tests/ --cov=src --cov-report=html
```

## 📖 客户端推荐

### Windows
- [Clash for Windows](https://github.com/Fndroid/clash_for_windows_pkg/releases)
- [V2RayN](https://github.com/2dust/v2rayN/releases)

### macOS
- [ClashX](https://github.com/yichengchen/clashX/releases)
- [V2RayU](https://github.com/yanue/V2rayU/releases)

### Linux
- [Clash for Windows](https://github.com/Fndroid/clash_for_windows_pkg/releases)
- [Qv2ray](https://github.com/Qv2ray/Qv2ray/releases)

### Android
- [Clash for Android](https://github.com/Kr328/ClashForAndroid/releases)
- [V2RayNG](https://github.com/2dust/v2rayNG/releases)

### iOS
- Shadowrocket（付费，App Store）
- Quantumult X（付费，App Store）

## 🔧 高级功能

### 自定义节点源

编辑 `config/sources.yaml` 添加你的节点源：

```yaml
subscription_sources:
  - name: "我的订阅源"
    url: "https://your-subscription-url"
    enabled: true
    type: "base64"
```

### 调整测速参数

编辑 `config/settings.yaml`：

```yaml
speed_test:
  timeout: 15           # 测速超时时间
  min_speed: 1.0        # 最低速度要求
  max_latency: 1000     # 最大延迟
  concurrent_tests: 50  # 并发数
```

### 过滤关键词

```yaml
filter:
  exclude_keywords:
    - "过期"
    - "expired"
    - "禁用"
```

## 🐛 常见问题

### 1. 测速功能不准确？

本项目的测速功能使用简化的 TCP 连接测试。生产环境建议：
- 在本地网络环境运行以获得准确结果
- 集成专业的测速工具如 LiteSpeedTest

### 2. GitHub Actions 运行失败？

检查：
- 仓库权限设置（需要 write 权限）
- 配置文件是否正确
- 节点源是否可访问

### 3. 节点数量太少？

- 检查节点源配置是否正确
- 尝试禁用测速（`--skip-test`）
- 调整过滤参数（最大延迟、最低速度）

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 📝 开发计划

- [ ] 集成专业测速工具（LiteSpeedTest）
- [ ] 添加 Web 界面
- [ ] 支持按地区筛选节点
- [ ] 节点质量评分系统
- [ ] 订阅历史记录功能
- [ ] 自定义规则过滤

## ⚠️ 免责声明

本项目仅供学习交流使用，请勿用于非法用途。使用本项目产生的任何后果由使用者自行承担。

## 📜 许可证

[MIT License](LICENSE)

## 🌟 Star History

如果这个项目对你有帮助，请给个 Star ⭐️

## 📬 联系方式

- 项目地址：https://github.com/miaolitao/V2Ray
- Issue 反馈：https://github.com/miaolitao/V2Ray/issues
- 参考项目：https://github.com/free-nodes/v2rayfree
- 参考项目：https://github.com/ermaozi/get_subscribe
---

**注意**：本项目收集的节点均来自互联网公开资源，节点质量和可用性无法保证。建议仅用于测试和学习目的。

