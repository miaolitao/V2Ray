"""节点收集器模块 - 从多个来源爬取节点"""

import asyncio
import base64
from typing import List, Dict, Any, Optional
import yaml
from utils.logger import get_logger
from utils.network import fetch_url
from .parser import NodeParser, Node

logger = get_logger()


class NodeCollector:
    """节点收集器 - 从订阅链接、GitHub 等来源收集节点"""
    
    def __init__(self, config_manager):
        """
        初始化节点收集器
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config = config_manager
        self.timeout = self.config.get_setting('general.timeout', 10)
        self.parser = NodeParser()
    
    async def collect_all(self) -> List[Node]:
        """
        从所有来源收集节点
        
        Returns:
            节点列表
        """
        logger.info("开始收集节点...")
        all_nodes = []
        
        # 收集订阅源
        subscription_sources = self.config.get_sources('subscription_sources')
        if subscription_sources:
            logger.info(f"收集订阅源: {len(subscription_sources)} 个")
            subscription_nodes = await self._collect_subscriptions(subscription_sources)
            all_nodes.extend(subscription_nodes)
        
        # 收集 GitHub 源
        github_sources = self.config.get_sources('github_sources')
        if github_sources:
            logger.info(f"收集 GitHub 源: {len(github_sources)} 个")
            github_nodes = await self._collect_github_sources(github_sources)
            all_nodes.extend(github_nodes)
        
        # 收集 Telegram 源（如果启用）
        telegram_sources = self.config.get_sources('telegram_sources')
        if telegram_sources:
            logger.info(f"收集 Telegram 源: {len(telegram_sources)} 个")
            telegram_nodes = await self._collect_telegram_sources(telegram_sources)
            all_nodes.extend(telegram_nodes)
        
        logger.info(f"节点收集完成，共收集 {len(all_nodes)} 个节点")
        return all_nodes
    
    async def _collect_subscriptions(self, sources: List[Dict[str, Any]]) -> List[Node]:
        """
        从订阅源收集节点
        
        Args:
            sources: 订阅源列表
        
        Returns:
            节点列表
        """
        tasks = [
            self._fetch_subscription(source)
            for source in sources
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_nodes = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"订阅源 {sources[i]['name']} 收集失败: {result}")
            elif result:
                all_nodes.extend(result)
        
        return all_nodes
    
    async def _fetch_subscription(self, source: Dict[str, Any]) -> List[Node]:
        """
        获取单个订阅源的节点
        
        Args:
            source: 订阅源配置
        
        Returns:
            节点列表
        """
        name = source.get('name', 'Unknown')
        url = source.get('url')
        source_type = source.get('type', 'base64')
        
        if not url:
            logger.warning(f"订阅源 {name} 缺少 URL")
            return []
        
        logger.info(f"正在获取订阅源: {name}")
        content = await fetch_url(url, timeout=self.timeout)
        
        if not content:
            logger.warning(f"订阅源 {name} 内容为空")
            return []
        
        nodes = []
        
        try:
            if source_type == 'base64':
                nodes = self._parse_base64_subscription(content)
            elif source_type == 'clash':
                nodes = self._parse_clash_subscription(content)
            else:
                logger.warning(f"不支持的订阅类型: {source_type}")
        
        except Exception as e:
            logger.error(f"解析订阅源 {name} 失败: {e}")
        
        logger.info(f"订阅源 {name} 获取到 {len(nodes)} 个节点")
        return nodes
    
    def _parse_base64_subscription(self, content: str) -> List[Node]:
        """
        解析 Base64 格式的订阅内容
        
        Args:
            content: 订阅内容
        
        Returns:
            节点列表
        """
        try:
            # 尝试 Base64 解码
            decoded = base64.b64decode(content).decode('utf-8')
        except Exception:
            # 如果解码失败，尝试直接使用原内容
            decoded = content
        
        # 分割成行，每行一个节点链接
        links = [line.strip() for line in decoded.split('\n') if line.strip()]
        
        # 解析节点
        nodes = []
        for link in links:
            node = self.parser.parse(link)
            if node:
                nodes.append(node)
        
        return nodes
    
    def _parse_clash_subscription(self, content: str) -> List[Node]:
        """
        解析 Clash 格式的订阅内容
        
        Args:
            content: 订阅内容（YAML）
        
        Returns:
            节点列表
        """
        try:
            config = yaml.safe_load(content)
            proxies = config.get('proxies', [])
            
            nodes = []
            for proxy in proxies:
                node = self._clash_proxy_to_node(proxy)
                if node:
                    nodes.append(node)
            
            return nodes
        
        except Exception as e:
            logger.error(f"解析 Clash 配置失败: {e}")
            return []
    
    def _clash_proxy_to_node(self, proxy: Dict[str, Any]) -> Optional[Node]:
        """
        将 Clash 代理配置转换为 Node 对象
        
        Args:
            proxy: Clash 代理配置
        
        Returns:
            节点对象
        """
        try:
            proxy_type = proxy.get('type', '').lower()
            
            if proxy_type == 'ss':
                return Node(
                    protocol='ss',
                    server=proxy.get('server', ''),
                    port=int(proxy.get('port', 0)),
                    password=proxy.get('password', ''),
                    method=proxy.get('cipher', ''),
                    name=proxy.get('name', 'SS节点'),
                    extra={}
                )
            
            elif proxy_type == 'ssr':
                return Node(
                    protocol='ssr',
                    server=proxy.get('server', ''),
                    port=int(proxy.get('port', 0)),
                    password=proxy.get('password', ''),
                    method=proxy.get('cipher', ''),
                    name=proxy.get('name', 'SSR节点'),
                    extra={
                        'protocol': proxy.get('protocol', ''),
                        'obfs': proxy.get('obfs', ''),
                        'obfs_param': proxy.get('obfs-param', ''),
                        'protocol_param': proxy.get('protocol-param', ''),
                    }
                )
            
            elif proxy_type == 'vmess':
                return Node(
                    protocol='vmess',
                    server=proxy.get('server', ''),
                    port=int(proxy.get('port', 0)),
                    password=proxy.get('uuid', ''),
                    method=proxy.get('cipher', 'auto'),
                    name=proxy.get('name', 'VMess节点'),
                    extra={
                        'aid': proxy.get('alterId', 0),
                        'net': proxy.get('network', 'tcp'),
                        'type': proxy.get('ws-opts', {}).get('headers', {}).get('type', 'none'),
                        'host': proxy.get('ws-opts', {}).get('headers', {}).get('Host', ''),
                        'path': proxy.get('ws-opts', {}).get('path', ''),
                        'tls': 'tls' if proxy.get('tls', False) else '',
                        'sni': proxy.get('servername', ''),
                    }
                )
            
            elif proxy_type == 'trojan':
                return Node(
                    protocol='trojan',
                    server=proxy.get('server', ''),
                    port=int(proxy.get('port', 0)),
                    password=proxy.get('password', ''),
                    method='',
                    name=proxy.get('name', 'Trojan节点'),
                    extra={
                        'sni': proxy.get('sni', ''),
                        'skip_cert_verify': proxy.get('skip-cert-verify', False),
                    }
                )
            
            elif proxy_type == 'vless':
                return Node(
                    protocol='vless',
                    server=proxy.get('server', ''),
                    port=int(proxy.get('port', 0)),
                    password=proxy.get('uuid', ''),
                    method=proxy.get('encryption', 'none'),
                    name=proxy.get('name', 'VLESS节点'),
                    extra={
                        'flow': proxy.get('flow', ''),
                        'type': proxy.get('network', 'tcp'),
                        'security': proxy.get('tls', 'none'),
                        'sni': proxy.get('servername', ''),
                    }
                )
            
            else:
                logger.debug(f"不支持的 Clash 代理类型: {proxy_type}")
                return None
        
        except Exception as e:
            logger.debug(f"转换 Clash 代理失败: {e}")
            return None
    
    async def _collect_github_sources(self, sources: List[Dict[str, Any]]) -> List[Node]:
        """
        从 GitHub 仓库收集节点
        
        Args:
            sources: GitHub 源列表
        
        Returns:
            节点列表
        """
        tasks = [
            self._fetch_github_source(source)
            for source in sources
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_nodes = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"GitHub 源 {sources[i]['name']} 收集失败: {result}")
            elif result:
                all_nodes.extend(result)
        
        return all_nodes
    
    async def _fetch_github_source(self, source: Dict[str, Any]) -> List[Node]:
        """
        获取单个 GitHub 源的节点
        
        Args:
            source: GitHub 源配置
        
        Returns:
            节点列表
        """
        name = source.get('name', 'Unknown')
        repo = source.get('repo')
        file = source.get('file')
        
        if not repo or not file:
            logger.warning(f"GitHub 源 {name} 配置不完整")
            return []
        
        # 构建 GitHub raw 文件 URL
        url = f"https://raw.githubusercontent.com/{repo}/main/{file}"
        
        logger.info(f"正在获取 GitHub 源: {name}")
        content = await fetch_url(url, timeout=self.timeout)
        
        if not content:
            # 尝试 master 分支
            url = f"https://raw.githubusercontent.com/{repo}/master/{file}"
            content = await fetch_url(url, timeout=self.timeout)
        
        if not content:
            logger.warning(f"GitHub 源 {name} 内容为空")
            return []
        
        # 尝试解析为 Base64
        nodes = self._parse_base64_subscription(content)
        
        logger.info(f"GitHub 源 {name} 获取到 {len(nodes)} 个节点")
        return nodes
    
    async def _collect_telegram_sources(self, sources: List[Dict[str, Any]]) -> List[Node]:
        """
        从 Telegram 频道收集节点（需要 Telegram API）
        
        Args:
            sources: Telegram 源列表
        
        Returns:
            节点列表
        """
        logger.info("Telegram 源收集功能暂未实现（需要配置 Telegram API）")
        return []

