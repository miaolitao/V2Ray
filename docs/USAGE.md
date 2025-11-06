# 使用说明

本文档详细介绍 V2Ray 节点聚合系统的使用方法。

## 目录

- [快速开始](#快速开始)
- [命令行使用](#命令行使用)
- [配置文件](#配置文件)
- [输出文件使用](#输出文件使用)
- [客户端配置](#客户端配置)
- [GitHub Actions 使用](#github-actions-使用)
- [常见问题](#常见问题)

## 快速开始

### 1. 安装系统

```bash
# 克隆仓库
git clone https://github.com/miaolitao/V2Ray.git
cd V2Ray

# 运行安装脚本
bash scripts/install.sh
```

### 2. 运行更新

```bash
# 使用 Makefile（推荐）
make update

# 或直接运行
python main.py
```

### 3. 使用节点

更新完成后，在 `output/` 目录下会生成多种格式的配置文件：

- `nodes.txt` - Base64 订阅链接
- `clash.yaml` - Clash 配置
- `v2ray.json` - V2Ray 配置
- `surge.conf` - Surge 配置
- `quantumult.conf` - Quantumult X 配置

## 命令行使用

### 基本命令

```bash
# 完整更新（收集、测速、生成所有格式）
python main.py

# 快速更新（跳过测速）
python main.py --skip-test

# 仅生成 Clash 配置
python main.py --format clash

# 自定义输出目录
python main.py --output-dir /path/to/output

# 限制节点数量
python main.py --max-nodes 100

# 调试模式
python main.py --log-level DEBUG
```

### 使用 Makefile

```bash
# 查看所有命令
make help

# 完整更新
make update

# 快速更新（跳过测速）
make update-quick

# 仅生成指定格式
make update-base64
make update-clash
make update-v2ray
make update-surge
make update-quantumult

# 查看统计信息
make stats

# 查看最近日志
make logs

# 清理文件
make clean
```

## 配置文件

### 节点源配置（config/sources.yaml）

添加或修改节点源：

```yaml
# Base64 订阅源
subscription_sources:
  - name: "我的订阅源"
    url: "https://example.com/sub"
    enabled: true
    type: "base64"
  
  # Clash 订阅源
  - name: "Clash 订阅"
    url: "https://example.com/clash"
    enabled: true
    type: "clash"

# GitHub 仓库源
github_sources:
  - name: "GitHub 节点"
    repo: "user/repository"
    file: "nodes.txt"
    enabled: true

# Telegram 频道源（需要配置 API）
telegram_sources:
  - channel: "@freev2ray"
    enabled: false
```

### 系统设置（config/settings.yaml）

#### 通用设置

```yaml
general:
  log_level: "INFO"        # 日志级别
  timeout: 10              # HTTP 超时时间（秒）
  max_workers: 10          # 最大并发数
```

#### 测速设置

```yaml
speed_test:
  enabled: true            # 是否启用测速
  timeout: 15              # 测速超时时间
  min_speed: 1.0           # 最低速度要求（MB/s）
  max_latency: 1000        # 最大延迟（ms）
  concurrent_tests: 50     # 并发测速数量
  filter_invalid: true     # 过滤无效节点
```

#### 输出设置

```yaml
output:
  max_nodes: 200                    # 最大节点数
  max_nodes_per_protocol: 50        # 每种协议最大节点数
  sort_by: "speed"                  # 排序方式：speed, latency
  formats:
    - base64
    - clash
    - v2ray
    - surge
    - quantumult
```

#### 过滤设置

```yaml
filter:
  exclude_keywords:         # 排除关键词
    - "过期"
    - "expired"
    - "禁用"
  include_protocols:        # 包含的协议
    - ss
    - ssr
    - vmess
    - trojan
    - vless
```

### Clash 模板（config/clash_template.yaml）

自定义 Clash 配置模板：

```yaml
port: 7890
socks-port: 7891
allow-lan: false
mode: rule

# 自定义代理组
proxy-groups:
  - name: "🚀 节点选择"
    type: select
    proxies:
      - "♻️ 自动选择"
      - DIRECT

  - name: "♻️ 自动选择"
    type: url-test
    url: http://www.gstatic.com/generate_204
    interval: 300
    proxies: []

# 自定义规则
rules:
  - DOMAIN-SUFFIX,google.com,🚀 节点选择
  - GEOIP,CN,DIRECT
  - MATCH,🚀 节点选择
```

## 输出文件使用

### Base64 订阅（nodes.txt）

**使用方法：**

1. 打开 `output/nodes.txt`
2. 复制全部内容
3. 在客户端中导入订阅

**适用客户端：**
- V2RayN (Windows)
- V2RayNG (Android)
- V2RayU (macOS)
- 大多数支持订阅的客户端

### Clash 配置（clash.yaml）

**本地使用：**

```bash
# 复制到 Clash 配置目录
cp output/clash.yaml ~/.config/clash/config.yaml

# 重启 Clash
```

**在线订阅：**

如果你的仓库是公开的，可以使用 GitHub Raw 链接作为订阅地址：

```
https://raw.githubusercontent.com/miaolitao/V2Ray/main/output/latest/clash.yaml
```

### V2Ray 配置（v2ray.json）

```bash
# 使用 V2Ray 配置
v2ray -config output/v2ray.json
```

### Surge 配置（surge.conf）

直接在 Surge 中导入配置文件。

### Quantumult X 配置（quantumult.conf）

在 Quantumult X 中导入配置文件。

## 客户端配置

### Windows - Clash for Windows

1. 下载并安装 [Clash for Windows](https://github.com/Fndroid/clash_for_windows_pkg/releases)
2. 打开 Clash for Windows
3. 点击 "配置" → "导入配置文件"
4. 选择 `output/clash.yaml`
5. 启用系统代理

### Windows - V2RayN

1. 下载并安装 [V2RayN](https://github.com/2dust/v2rayN/releases)
2. 打开 V2RayN
3. 点击 "订阅" → "订阅设置"
4. 添加订阅地址（使用 nodes.txt 的内容或在线链接）
5. 更新订阅
6. 选择节点并启用代理

### macOS - ClashX

1. 下载并安装 [ClashX](https://github.com/yichengchen/clashX/releases)
2. 打开 ClashX
3. 点击 "配置" → "打开配置文件夹"
4. 将 `clash.yaml` 复制到配置文件夹
5. 在 ClashX 中选择该配置
6. 启用系统代理

### Android - Clash for Android

1. 安装 [Clash for Android](https://github.com/Kr328/ClashForAndroid/releases)
2. 打开应用
3. 点击 "配置" → "从文件导入"
4. 选择 `clash.yaml`
5. 启动服务

### iOS - Shadowrocket

1. 在 App Store 购买并安装 Shadowrocket
2. 打开应用
3. 点击右上角 "+"
4. 选择 "类型" → "Subscribe"
5. 粘贴订阅链接（Base64 格式）
6. 保存并更新订阅

## GitHub Actions 使用

### 启用自动更新

1. Fork 本仓库
2. 进入 Settings → Actions → General
3. 启用 "Read and write permissions"
4. Actions 将每 6 小时自动运行

### 手动触发更新

1. 进入仓库的 "Actions" 页面
2. 选择 "更新节点" 工作流
3. 点击 "Run workflow"
4. 配置选项：
   - **跳过测速**：是否跳过速度测试
   - **输出格式**：选择要生成的格式
5. 点击 "Run workflow" 执行

### 修改更新频率

编辑 `.github/workflows/update-nodes.yml`：

```yaml
on:
  schedule:
    # 每 6 小时运行一次
    - cron: '0 */6 * * *'
    
    # 修改为每 3 小时运行一次
    # - cron: '0 */3 * * *'
    
    # 修改为每天凌晨 2 点运行
    # - cron: '0 2 * * *'
```

### 查看运行日志

1. 进入 "Actions" 页面
2. 点击最近的运行记录
3. 查看各个步骤的日志
4. 下载产物（输出文件和日志）

## 常见问题

### Q1: 如何添加自己的节点源？

编辑 `config/sources.yaml`，添加新的源：

```yaml
subscription_sources:
  - name: "我的源"
    url: "https://your-url"
    enabled: true
    type: "base64"
```

### Q2: 测速太慢怎么办？

有几种方法：

1. 跳过测速：
```bash
python main.py --skip-test
```

2. 减少并发测速数量（编辑 `config/settings.yaml`）：
```yaml
speed_test:
  concurrent_tests: 20  # 降低并发数
```

3. 减少超时时间：
```yaml
speed_test:
  timeout: 10  # 降低超时时间
```

### Q3: 节点数量太少？

1. 禁用测速：
```bash
python main.py --skip-test
```

2. 放宽过滤条件（编辑 `config/settings.yaml`）：
```yaml
speed_test:
  min_speed: 0.5      # 降低速度要求
  max_latency: 2000   # 提高延迟上限
  filter_invalid: false # 不过滤无效节点
```

3. 增加节点源：编辑 `config/sources.yaml` 添加更多源

### Q4: 如何只更新特定格式？

```bash
# 只生成 Clash 配置
python main.py --format clash

# 或使用 Makefile
make update-clash
```

### Q5: GitHub Actions 运行失败？

检查：

1. 仓库权限：Settings → Actions → General → Workflow permissions
   - 选择 "Read and write permissions"

2. 配置文件：确保 `config/` 目录下的配置文件正确

3. 查看日志：Actions 页面查看详细错误信息

### Q6: 如何在本地测试配置？

```bash
# 使用调试模式
python main.py --log-level DEBUG

# 检查配置文件
python -c "from src.config_manager import ConfigManager; c = ConfigManager(); print(c.settings)"
```

### Q7: 输出的节点无法使用？

可能的原因：

1. 节点本身已失效（免费节点经常变动）
2. 测速功能在 GitHub Actions 环境运行（美国服务器），本地可用性可能不同
3. 需要在本地运行测速获得准确结果

建议：
- 在本地运行 `make update`
- 尝试更多节点源
- 检查客户端配置是否正确

## 更多帮助

如有其他问题，请：

1. 查看 [项目文档](../README.md)
2. 提交 [Issue](https://github.com/miaolitao/V2Ray/issues)
3. 查看现有的 [Issue](https://github.com/miaolitao/V2Ray/issues) 和讨论

