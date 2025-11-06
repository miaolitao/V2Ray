# 项目结构说明

本文档详细说明了项目的目录结构和文件组织。

## 完整目录树

```
V2Ray/
├── .github/                    # GitHub 相关配置
│   └── workflows/              # GitHub Actions 工作流
│       ├── update-nodes.yml    # 定时更新节点
│       └── test.yml            # 自动化测试
│
├── config/                     # 配置文件目录
│   ├── sources.yaml            # 节点源配置
│   ├── settings.yaml           # 系统设置
│   └── clash_template.yaml     # Clash 配置模板
│
├── src/                        # 核心源代码
│   ├── __init__.py             # 模块初始化
│   ├── parser.py               # 节点解析器（SS/SSR/VMess/Trojan/VLESS）
│   ├── collector.py            # 节点收集器（订阅源/GitHub）
│   ├── deduplicator.py         # 去重模块
│   ├── formatter.py            # 格式转换器（Base64/Clash/V2Ray/Surge/Quantumult）
│   ├── speed_tester.py         # 测速模块
│   └── config_manager.py       # 配置管理器
│
├── utils/                      # 工具模块
│   ├── __init__.py             # 模块初始化
│   ├── logger.py               # 日志工具（彩色日志/文件日志）
│   ├── network.py              # 网络工具（HTTP请求/连通性测试）
│   └── validator.py            # 验证工具（节点验证/URL验证）
│
├── tests/                      # 测试文件
│   ├── __init__.py             # 测试模块初始化
│   ├── test_parser.py          # 解析器测试
│   ├── test_collector.py       # 收集器测试
│   ├── test_deduplicator.py    # 去重模块测试
│   ├── test_formatter.py       # 格式转换测试
│   └── test_config_manager.py  # 配置管理测试
│
├── scripts/                    # 脚本文件
│   └── install.sh              # 安装脚本
│
├── docs/                       # 文档目录
│   ├── USAGE.md                # 使用说明
│   ├── DEVELOPMENT.md          # 开发文档
│   └── PROJECT_STRUCTURE.md    # 项目结构说明（本文件）
│
├── output/                     # 输出文件目录
│   ├── nodes.txt               # Base64 格式节点
│   ├── clash.yaml              # Clash 配置
│   ├── v2ray.json              # V2Ray 配置
│   ├── surge.conf              # Surge 配置
│   ├── quantumult.conf         # Quantumult X 配置
│   └── stats.json              # 统计信息
│
├── logs/                       # 日志目录
│   └── update_*.log            # 运行日志
│
├── main.py                     # 主程序入口
├── Makefile                    # Make 命令配置
├── pyproject.toml              # 项目配置（uv）
├── requirements.txt            # Python 依赖列表
├── .gitignore                  # Git 忽略文件
├── .python-version             # Python 版本标识
├── LICENSE                     # 许可证
└── README.md                   # 项目说明
```

## 核心模块详解

### 1. 节点解析器（src/parser.py）

**职责**：解析各种协议的节点链接

**类**：
- `Node`：节点数据结构
- `NodeParser`：节点解析器

**支持协议**：
- SS (Shadowsocks)
- SSR (ShadowsocksR)
- VMess
- Trojan
- VLESS

**关键方法**：
- `parse(link)` - 解析单个节点链接
- `parse_batch(links)` - 批量解析

### 2. 节点收集器（src/collector.py）

**职责**：从多个来源收集节点

**类**：
- `NodeCollector`：节点收集器

**支持来源**：
- 订阅链接（Base64/Clash）
- GitHub 仓库
- Telegram 频道（待实现）

**关键方法**：
- `collect_all()` - 收集所有源的节点
- `_collect_subscriptions()` - 收集订阅源
- `_collect_github_sources()` - 收集 GitHub 源

### 3. 去重模块（src/deduplicator.py）

**职责**：移除重复节点并过滤

**类**：
- `Deduplicator`：去重器

**去重策略**：
- 基于配置哈希
- 基于服务器地址
- 组合策略

**关键方法**：
- `remove_duplicates()` - 去重
- `filter_by_keywords()` - 关键词过滤
- `limit_nodes_per_protocol()` - 限制每种协议数量

### 4. 格式转换器（src/formatter.py）

**职责**：将节点转换为各种客户端格式

**类**：
- `Formatter`：格式转换器

**支持格式**：
- Base64 订阅
- Clash YAML
- V2Ray JSON
- Surge
- Quantumult X

**关键方法**：
- `to_base64()` - Base64 格式
- `to_clash_yaml()` - Clash 格式
- `to_v2ray_json()` - V2Ray 格式
- `to_surge()` - Surge 格式
- `to_quantumult()` - Quantumult X 格式

### 5. 测速模块（src/speed_tester.py）

**职责**：测试节点速度和可用性

**类**：
- `TestResult`：测速结果
- `SpeedTester`：测速器

**测试指标**：
- 连通性
- 延迟（TCP 连接时间）
- 速度（估算）

**关键方法**：
- `test_all()` - 测试所有节点
- `test_node()` - 测试单个节点
- `filter_by_test_results()` - 过滤结果
- `sort_results()` - 排序结果

### 6. 配置管理器（src/config_manager.py）

**职责**：管理配置文件

**类**：
- `ConfigManager`：配置管理器

**管理的配置**：
- 系统设置
- 节点源配置
- Clash 模板

**关键方法**：
- `get_setting()` - 获取设置
- `get_sources()` - 获取节点源
- `get_clash_template()` - 获取 Clash 模板

## 工具模块详解

### 1. 日志工具（utils/logger.py）

**功能**：
- 彩色控制台输出
- 文件日志记录
- 多级别日志

**函数**：
- `setup_logger()` - 设置日志记录器
- `get_logger()` - 获取日志记录器

### 2. 网络工具（utils/network.py）

**功能**：
- 异步/同步 HTTP 请求
- 连通性测试
- 自动重试

**函数**：
- `fetch_url()` - 异步获取 URL
- `fetch_content()` - 同步获取内容
- `test_connectivity()` - 测试连通性

### 3. 验证工具（utils/validator.py）

**功能**：
- URL 验证
- IP 地址验证
- 域名验证
- 节点数据验证

**函数**：
- `validate_url()` - 验证 URL
- `validate_ip()` - 验证 IP
- `validate_domain()` - 验证域名
- `validate_node()` - 验证节点
- `sanitize_name()` - 清理名称

## 配置文件详解

### 1. 节点源配置（config/sources.yaml）

定义节点来源：

```yaml
subscription_sources:      # 订阅源
github_sources:            # GitHub 源
telegram_sources:          # Telegram 源
crawl_config:             # 爬取配置
```

### 2. 系统设置（config/settings.yaml）

系统运行参数：

```yaml
general:          # 通用设置
speed_test:       # 测速配置
output:           # 输出配置
deduplication:    # 去重配置
filter:           # 过滤配置
clash_template:   # Clash 模板配置
```

### 3. Clash 模板（config/clash_template.yaml）

Clash 配置模板：

```yaml
port:             # HTTP 代理端口
socks-port:       # SOCKS5 代理端口
proxies:          # 代理节点（自动填充）
proxy-groups:     # 代理组
rules:            # 路由规则
```

## 输出文件详解

### 1. Base64 订阅（output/nodes.txt）

Base64 编码的节点链接，每行一个节点。

### 2. Clash 配置（output/clash.yaml）

完整的 Clash YAML 配置文件。

### 3. V2Ray 配置（output/v2ray.json）

V2Ray JSON 格式配置。

### 4. Surge 配置（output/surge.conf）

Surge 配置文件。

### 5. Quantumult X 配置（output/quantumult.conf）

Quantumult X 配置文件。

### 6. 统计信息（output/stats.json）

运行统计信息：

```json
{
  "update_time": "2024-01-01 12:00:00",
  "total_nodes": 150,
  "protocols": {
    "ss": 50,
    "vmess": 80,
    "trojan": 20
  }
}
```

## 工作流文件详解

### 1. 更新节点（.github/workflows/update-nodes.yml）

**触发条件**：
- 定时（每 6 小时）
- 手动触发

**执行步骤**：
1. 检出代码
2. 设置 Python 环境
3. 安装 uv 和依赖
4. 运行节点更新
5. 提交更新
6. 上传产物

### 2. 自动测试（.github/workflows/test.yml）

**触发条件**：
- Push 到 main/master
- Pull Request

**执行步骤**：
1. 多平台测试（Ubuntu, macOS）
2. 多版本测试（Python 3.9, 3.10, 3.11）
3. 运行测试套件
4. 上传覆盖率

## 开发工作流

```
1. 本地开发
   ├── 修改代码
   ├── 运行测试
   ├── 代码检查
   └── 提交更改

2. CI/CD
   ├── Push 触发测试
   ├── 测试通过
   ├── 定时更新节点
   └── 自动提交结果

3. 发布
   ├── 创建 Release
   ├── 生成 Tag
   └── 发布说明
```

## 数据流向图

```
外部源 → Collector → Parser → Node 对象
                                  ↓
                            Deduplicator
                                  ↓
                            SpeedTester
                                  ↓
                             Formatter
                                  ↓
                          输出文件 (各种格式)
```

## 扩展点

如果要扩展项目功能，可以在以下位置添加：

1. **新协议支持**
   - `src/parser.py` - 添加解析方法
   - `src/formatter.py` - 添加转换方法

2. **新节点源**
   - `src/collector.py` - 添加收集方法
   - `config/sources.yaml` - 添加源配置

3. **新输出格式**
   - `src/formatter.py` - 添加格式转换方法
   - `main.py` - 添加命令行选项

4. **新功能模块**
   - 在 `src/` 下创建新模块
   - 在 `main.py` 中集成
   - 添加配置支持
   - 编写测试

## 依赖关系

```
main.py
  ├── ConfigManager
  ├── NodeCollector
  │   ├── NodeParser
  │   └── network utils
  ├── Deduplicator
  ├── SpeedTester
  │   └── network utils
  └── Formatter
      └── ConfigManager
```

## 总结

项目采用模块化设计，各模块职责清晰，易于维护和扩展。核心流程为：收集 → 解析 → 去重 → 测速 → 格式转换，每个步骤都可以独立配置和优化。

