# 开发文档

本文档面向开发者，介绍项目的技术架构、开发规范和贡献指南。

## 目录

- [技术栈](#技术栈)
- [项目架构](#项目架构)
- [开发环境设置](#开发环境设置)
- [代码规范](#代码规范)
- [测试](#测试)
- [贡献指南](#贡献指南)

## 技术栈

### 核心技术

- **Python 3.9+**：主要开发语言
- **asyncio**：异步 I/O 框架
- **aiohttp**：异步 HTTP 客户端
- **PyYAML**：YAML 配置文件解析
- **pydantic**：数据验证

### 包管理

- **uv**：快速的 Python 包管理器

### 测试

- **pytest**：测试框架
- **pytest-asyncio**：异步测试支持
- **pytest-cov**：代码覆盖率

### CI/CD

- **GitHub Actions**：自动化工作流

## 项目架构

### 目录结构

```
V2Ray/
├── src/                    # 核心模块
│   ├── parser.py           # 节点解析器
│   ├── collector.py        # 节点收集器
│   ├── deduplicator.py     # 去重模块
│   ├── formatter.py        # 格式转换器
│   ├── speed_tester.py     # 测速模块
│   └── config_manager.py   # 配置管理
├── utils/                  # 工具模块
│   ├── logger.py           # 日志工具
│   ├── network.py          # 网络工具
│   └── validator.py        # 验证工具
├── tests/                  # 测试文件
├── config/                 # 配置文件
└── main.py                 # 主程序入口
```

### 核心模块说明

#### 1. NodeParser（parser.py）

**职责**：解析各种协议的节点链接

**支持的协议**：
- Shadowsocks (ss://)
- ShadowsocksR (ssr://)
- VMess (vmess://)
- Trojan (trojan://)
- VLESS (vless://)

**主要方法**：
```python
class NodeParser:
    @staticmethod
    def parse(link: str) -> Optional[Node]
    
    @staticmethod
    def parse_batch(links: List[str]) -> List[Node]
```

#### 2. NodeCollector（collector.py）

**职责**：从多个来源收集节点

**支持的源类型**：
- 订阅链接（Base64、Clash YAML）
- GitHub 仓库
- Telegram 频道（待实现）

**主要方法**：
```python
class NodeCollector:
    async def collect_all(self) -> List[Node]
    async def _collect_subscriptions(self, sources) -> List[Node]
    async def _collect_github_sources(self, sources) -> List[Node]
```

#### 3. Deduplicator（deduplicator.py）

**职责**：移除重复节点

**去重策略**：
- 基于配置哈希
- 基于服务器地址和端口
- 组合策略

**主要方法**：
```python
class Deduplicator:
    def remove_duplicates(self, nodes, speed_results=None) -> List[Node]
    def filter_by_keywords(self, nodes, exclude_keywords, include_keywords) -> List[Node]
    def limit_nodes_per_protocol(self, nodes, max_per_protocol) -> List[Node]
```

#### 4. Formatter（formatter.py）

**职责**：将节点转换为各种客户端格式

**支持的格式**：
- Base64 订阅
- Clash YAML
- V2Ray JSON
- Surge
- Quantumult X

**主要方法**：
```python
class Formatter:
    def to_base64(self, nodes) -> str
    def to_clash_yaml(self, nodes, template=None) -> str
    def to_v2ray_json(self, nodes) -> str
    def to_surge(self, nodes) -> str
    def to_quantumult(self, nodes) -> str
```

#### 5. SpeedTester（speed_tester.py）

**职责**：测试节点速度和可用性

**测试方法**：
- TCP 连接测试（延迟）
- 简化速度估算

**注意**：当前实现为简化版本，生产环境建议集成专业工具如 LiteSpeedTest

**主要方法**：
```python
class SpeedTester:
    async def test_all(self, nodes) -> List[TestResult]
    async def test_node(self, node) -> TestResult
    def filter_by_test_results(self, results) -> List[TestResult]
    def sort_results(self, results, sort_by) -> List[TestResult]
```

#### 6. ConfigManager（config_manager.py）

**职责**：管理配置文件

**配置文件**：
- sources.yaml：节点源配置
- settings.yaml：系统设置
- clash_template.yaml：Clash 模板

**主要方法**：
```python
class ConfigManager:
    def get_setting(self, key, default=None) -> Any
    def get_sources(self, source_type=None) -> list
    def get_clash_template(self) -> Dict[str, Any]
```

### 数据流程

```
1. 收集阶段
   ├── NodeCollector.collect_all()
   ├── 从多个源获取节点链接
   └── 返回原始链接列表

2. 解析阶段
   ├── NodeParser.parse_batch()
   ├── 解析各种协议链接
   └── 返回 Node 对象列表

3. 去重阶段
   ├── Deduplicator.remove_duplicates()
   ├── 基于哈希/地址去重
   ├── 关键词过滤
   └── 返回唯一节点列表

4. 测速阶段（可选）
   ├── SpeedTester.test_all()
   ├── 并发测试节点
   ├── 过滤和排序
   └── 返回可用节点列表

5. 格式转换阶段
   ├── Formatter.to_xxx()
   ├── 转换为各种格式
   └── 保存到文件
```

## 开发环境设置

### 1. 克隆仓库

```bash
git clone https://github.com/your-username/V2Ray.git
cd V2Ray
```

### 2. 安装 uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. 安装依赖

```bash
# 安装项目依赖
uv pip install -e .

# 安装开发依赖
uv pip install -e ".[dev]"
```

### 4. 配置 IDE

#### VS Code

推荐安装扩展：
- Python
- Pylance
- Python Test Explorer

推荐设置（.vscode/settings.json）：
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"]
}
```

#### PyCharm

1. 设置 Python 解释器
2. 启用 pytest 作为测试框架
3. 配置代码格式化工具（Black）

## 代码规范

### Python 代码风格

遵循 [PEP 8](https://pep8.org/) 规范：

```python
# 使用 4 个空格缩进
def function_name(param1, param2):
    """函数文档字符串"""
    result = param1 + param2
    return result

# 类名使用驼峰命名
class MyClass:
    """类文档字符串"""
    
    def __init__(self):
        self.value = 0
```

### 命名规范

- **变量和函数**：snake_case
  - `node_list`
  - `parse_node()`
  
- **类名**：PascalCase
  - `NodeParser`
  - `SpeedTester`
  
- **常量**：UPPER_SNAKE_CASE
  - `MAX_NODES`
  - `DEFAULT_TIMEOUT`

### 类型注解

使用类型注解提高代码可读性：

```python
from typing import List, Optional, Dict, Any

def process_nodes(nodes: List[Node], max_count: int = 100) -> List[Node]:
    """处理节点列表"""
    return nodes[:max_count]

async def fetch_url(url: str) -> Optional[str]:
    """获取 URL 内容"""
    ...
```

### 文档字符串

使用 Google 风格的文档字符串：

```python
def complex_function(param1: str, param2: int) -> Dict[str, Any]:
    """
    简短描述
    
    详细描述（可选）
    
    Args:
        param1: 参数1的说明
        param2: 参数2的说明
    
    Returns:
        返回值说明
    
    Raises:
        ValueError: 错误情况说明
    """
    ...
```

### 代码格式化

使用 Black 格式化代码：

```bash
# 格式化所有代码
make format

# 或手动运行
black src/ utils/ tests/
```

### 代码检查

使用 ruff 进行代码检查：

```bash
# 检查代码
make lint

# 或手动运行
ruff check src/ utils/ tests/
```

## 测试

### 运行测试

```bash
# 运行所有测试
make test

# 或使用 pytest
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_parser.py -v

# 运行特定测试
pytest tests/test_parser.py::TestNodeParser::test_parse_ss_link -v
```

### 测试覆盖率

```bash
# 生成覆盖率报告
pytest tests/ --cov=src --cov-report=html

# 查看报告
open htmlcov/index.html
```

### 编写测试

测试文件放在 `tests/` 目录，文件名以 `test_` 开头：

```python
# tests/test_example.py
import pytest
from src.parser import NodeParser

class TestNodeParser:
    """NodeParser 测试类"""
    
    def test_parse_ss_link(self):
        """测试 SS 链接解析"""
        link = "ss://..."
        node = NodeParser.parse(link)
        
        assert node is not None
        assert node.protocol == "ss"
    
    @pytest.mark.asyncio
    async def test_async_function(self):
        """测试异步函数"""
        result = await some_async_function()
        assert result is not None
```

### 测试用例编写原则

1. **独立性**：每个测试应该独立运行
2. **可重复性**：多次运行应得到相同结果
3. **清晰性**：测试名称应清楚说明测试内容
4. **完整性**：测试正常情况和异常情况

## 贡献指南

### 提交 Issue

提交 Issue 时请包含：

1. **问题描述**：清楚描述问题
2. **复现步骤**：如何复现问题
3. **预期行为**：期望的结果
4. **实际行为**：实际发生的情况
5. **环境信息**：
   - Python 版本
   - 操作系统
   - 相关配置

### 提交 Pull Request

1. Fork 仓库

2. 创建特性分支：
```bash
git checkout -b feature/my-feature
```

3. 进行开发：
   - 遵循代码规范
   - 添加测试
   - 更新文档

4. 运行测试：
```bash
make test
make lint
```

5. 提交更改：
```bash
git add .
git commit -m "feat: 添加新功能"
```

提交信息格式：
- `feat: 新功能`
- `fix: 修复问题`
- `docs: 文档更新`
- `test: 测试相关`
- `refactor: 代码重构`
- `style: 代码格式`
- `chore: 其他更改`

6. 推送到 GitHub：
```bash
git push origin feature/my-feature
```

7. 创建 Pull Request

### Pull Request 检查清单

- [ ] 代码遵循项目规范
- [ ] 添加了必要的测试
- [ ] 所有测试通过
- [ ] 更新了相关文档
- [ ] 提交信息清晰明确

## 常见开发任务

### 添加新的节点协议支持

1. 在 `NodeParser` 中添加解析方法
2. 在 `Formatter` 中添加转换方法
3. 更新 Node 数据结构（如需要）
4. 添加测试用例
5. 更新文档

### 添加新的输出格式

1. 在 `Formatter` 中添加转换方法
2. 在配置文件中添加格式选项
3. 在主程序中添加处理逻辑
4. 添加测试用例
5. 更新文档

### 优化测速功能

当前测速功能较简单，可以：

1. 集成专业测速工具（如 LiteSpeedTest）
2. 实现真实的代理速度测试
3. 添加更多测速指标
4. 优化并发控制

## 技术债务和改进方向

### 当前限制

1. 测速功能简化，未实现真实代理测试
2. Telegram 源收集未实现
3. 缺少 Web 界面
4. 缺少节点历史记录

### 改进方向

1. **测速优化**
   - 集成 LiteSpeedTest
   - 实现真实速度测试
   - 添加多种测试策略

2. **功能扩展**
   - 实现 Telegram Bot 集成
   - 添加 Web 管理界面
   - 支持节点订阅管理
   - 添加节点质量评分

3. **性能优化**
   - 使用数据库存储节点
   - 实现增量更新
   - 优化内存使用

4. **代码质量**
   - 提高测试覆盖率（目标 >80%）
   - 添加性能测试
   - 优化错误处理

## 联系方式

- 项目地址：https://github.com/your-username/V2Ray
- Issue：https://github.com/your-username/V2Ray/issues
- Discussions：https://github.com/your-username/V2Ray/discussions

欢迎贡献代码！🎉

