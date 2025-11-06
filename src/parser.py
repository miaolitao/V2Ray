"""节点解析器模块 - 支持多种协议"""

import base64
import json
import re
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse, parse_qs, unquote
from dataclasses import dataclass, asdict
from utils.logger import get_logger
from utils.validator import validate_node, sanitize_name

logger = get_logger()


@dataclass
class Node:
    """节点数据结构"""
    protocol: str  # ss, ssr, vmess, trojan, vless
    server: str
    port: int
    password: str = ""
    method: str = ""  # 加密方法
    name: str = "未命名节点"
    extra: Dict[str, Any] = None  # 协议特定参数
    raw_link: str = ""
    
    def __post_init__(self):
        if self.extra is None:
            self.extra = {}
        self.name = sanitize_name(self.name)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    def get_hash(self) -> str:
        """获取节点哈希值（用于去重）"""
        hash_str = f"{self.protocol}:{self.server}:{self.port}:{self.password}:{self.method}"
        return str(hash(hash_str))


class NodeParser:
    """节点解析器 - 解析各种协议的节点链接"""
    
    @staticmethod
    def parse(link: str) -> Optional[Node]:
        """
        解析节点链接
        
        Args:
            link: 节点链接
        
        Returns:
            解析后的节点对象，失败返回 None
        """
        link = link.strip()
        
        try:
            if link.startswith('ss://'):
                return NodeParser._parse_ss(link)
            elif link.startswith('ssr://'):
                return NodeParser._parse_ssr(link)
            elif link.startswith('vmess://'):
                return NodeParser._parse_vmess(link)
            elif link.startswith('trojan://'):
                return NodeParser._parse_trojan(link)
            elif link.startswith('vless://'):
                return NodeParser._parse_vless(link)
            else:
                logger.debug(f"不支持的协议: {link[:20]}...")
                return None
        except Exception as e:
            logger.debug(f"解析节点失败: {e}, 链接: {link[:50]}...")
            return None
    
    @staticmethod
    def _parse_ss(link: str) -> Optional[Node]:
        """
        解析 Shadowsocks 链接
        格式: ss://base64(method:password)@server:port#name
        或: ss://base64(method:password@server:port)#name
        """
        try:
            # 移除协议头
            link = link[5:]
            
            # 提取备注名称
            name = "SS节点"
            if '#' in link:
                link, name = link.split('#', 1)
                name = unquote(name)
            
            # Base64 解码
            try:
                decoded = base64.urlsafe_b64decode(link + '=' * (4 - len(link) % 4)).decode('utf-8')
            except Exception:
                # 尝试标准 Base64
                decoded = base64.b64decode(link + '=' * (4 - len(link) % 4)).decode('utf-8')
            
            # 解析格式1: method:password@server:port
            if '@' in decoded:
                method_password, server_port = decoded.split('@', 1)
                method, password = method_password.split(':', 1)
                server, port = server_port.rsplit(':', 1)
                
                node = Node(
                    protocol='ss',
                    server=server,
                    port=int(port),
                    password=password,
                    method=method,
                    name=name,
                    raw_link=f"ss://{link}"
                )
                
                if validate_node(node.to_dict()):
                    return node
        
        except Exception as e:
            logger.debug(f"SS 解析失败: {e}")
        
        return None
    
    @staticmethod
    def _parse_ssr(link: str) -> Optional[Node]:
        """
        解析 ShadowsocksR 链接
        格式: ssr://base64(server:port:protocol:method:obfs:base64pass/?params)
        """
        try:
            # 移除协议头
            link = link[6:]
            
            # Base64 解码
            try:
                decoded = base64.urlsafe_b64decode(link + '=' * (4 - len(link) % 4)).decode('utf-8')
            except Exception:
                decoded = base64.b64decode(link + '=' * (4 - len(link) % 4)).decode('utf-8')
            
            # 分离主体和参数
            main_part = decoded
            params = {}
            if '?' in decoded:
                main_part, param_str = decoded.split('?', 1)
                # 解析参数
                for param in param_str.split('&'):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        try:
                            params[key] = base64.urlsafe_b64decode(
                                value + '=' * (4 - len(value) % 4)
                            ).decode('utf-8')
                        except Exception:
                            params[key] = value
            
            # 解析主体: server:port:protocol:method:obfs:password_base64
            parts = main_part.split(':')
            if len(parts) >= 6:
                server, port, protocol, method, obfs, password_b64 = parts[:6]
                
                # 解码密码
                try:
                    password = base64.urlsafe_b64decode(
                        password_b64 + '=' * (4 - len(password_b64) % 4)
                    ).decode('utf-8')
                except Exception:
                    password = password_b64
                
                name = params.get('remarks', 'SSR节点')
                
                node = Node(
                    protocol='ssr',
                    server=server,
                    port=int(port),
                    password=password,
                    method=method,
                    name=name,
                    extra={
                        'protocol': protocol,
                        'obfs': obfs,
                        'obfs_param': params.get('obfsparam', ''),
                        'protocol_param': params.get('protoparam', ''),
                    },
                    raw_link=f"ssr://{link}"
                )
                
                if validate_node(node.to_dict()):
                    return node
        
        except Exception as e:
            logger.debug(f"SSR 解析失败: {e}")
        
        return None
    
    @staticmethod
    def _parse_vmess(link: str) -> Optional[Node]:
        """
        解析 VMess 链接
        格式: vmess://base64(json)
        """
        try:
            # 移除协议头
            link = link[8:]
            
            # Base64 解码
            try:
                decoded = base64.urlsafe_b64decode(link + '=' * (4 - len(link) % 4)).decode('utf-8')
            except Exception:
                decoded = base64.b64decode(link + '=' * (4 - len(link) % 4)).decode('utf-8')
            
            # 解析 JSON
            config = json.loads(decoded)
            
            node = Node(
                protocol='vmess',
                server=config.get('add', ''),
                port=int(config.get('port', 0)),
                password=config.get('id', ''),  # UUID
                method=config.get('scy', 'auto'),  # 加密方式
                name=config.get('ps', 'VMess节点'),
                extra={
                    'aid': config.get('aid', 0),  # alterId
                    'net': config.get('net', 'tcp'),  # 传输协议
                    'type': config.get('type', 'none'),  # 伪装类型
                    'host': config.get('host', ''),
                    'path': config.get('path', ''),
                    'tls': config.get('tls', ''),
                    'sni': config.get('sni', ''),
                    'alpn': config.get('alpn', ''),
                },
                raw_link=f"vmess://{link}"
            )
            
            if validate_node(node.to_dict()):
                return node
        
        except Exception as e:
            logger.debug(f"VMess 解析失败: {e}")
        
        return None
    
    @staticmethod
    def _parse_trojan(link: str) -> Optional[Node]:
        """
        解析 Trojan 链接
        格式: trojan://password@server:port?params#name
        """
        try:
            # 移除协议头
            link = link[9:]
            
            # 提取备注名称
            name = "Trojan节点"
            if '#' in link:
                link, name = link.split('#', 1)
                name = unquote(name)
            
            # 分离主体和参数
            main_part = link
            params = {}
            if '?' in link:
                main_part, param_str = link.split('?', 1)
                params = dict(param.split('=', 1) for param in param_str.split('&') if '=' in param)
            
            # 解析主体: password@server:port
            password, server_port = main_part.split('@', 1)
            server, port = server_port.rsplit(':', 1)
            
            node = Node(
                protocol='trojan',
                server=server,
                port=int(port),
                password=password,
                method='',
                name=name,
                extra={
                    'sni': params.get('sni', params.get('peer', '')),
                    'type': params.get('type', 'tcp'),
                    'security': params.get('security', 'tls'),
                    'skip_cert_verify': params.get('allowInsecure', '0') == '1',
                },
                raw_link=f"trojan://{link}"
            )
            
            if validate_node(node.to_dict()):
                return node
        
        except Exception as e:
            logger.debug(f"Trojan 解析失败: {e}")
        
        return None
    
    @staticmethod
    def _parse_vless(link: str) -> Optional[Node]:
        """
        解析 VLESS 链接
        格式: vless://uuid@server:port?params#name
        """
        try:
            # 移除协议头
            link = link[8:]
            
            # 提取备注名称
            name = "VLESS节点"
            if '#' in link:
                link, name = link.split('#', 1)
                name = unquote(name)
            
            # 分离主体和参数
            main_part = link
            params = {}
            if '?' in link:
                main_part, param_str = link.split('?', 1)
                params = dict(param.split('=', 1) for param in param_str.split('&') if '=' in param)
            
            # 解析主体: uuid@server:port
            uuid, server_port = main_part.split('@', 1)
            server, port = server_port.rsplit(':', 1)
            
            node = Node(
                protocol='vless',
                server=server,
                port=int(port),
                password=uuid,  # VLESS 使用 UUID
                method=params.get('encryption', 'none'),
                name=name,
                extra={
                    'flow': params.get('flow', ''),
                    'type': params.get('type', 'tcp'),
                    'security': params.get('security', 'none'),
                    'sni': params.get('sni', params.get('peer', '')),
                    'alpn': params.get('alpn', ''),
                    'fp': params.get('fp', ''),
                },
                raw_link=f"vless://{link}"
            )
            
            if validate_node(node.to_dict()):
                return node
        
        except Exception as e:
            logger.debug(f"VLESS 解析失败: {e}")
        
        return None
    
    @staticmethod
    def parse_batch(links: List[str]) -> List[Node]:
        """
        批量解析节点链接
        
        Args:
            links: 节点链接列表
        
        Returns:
            解析成功的节点列表
        """
        nodes = []
        for link in links:
            node = NodeParser.parse(link)
            if node:
                nodes.append(node)
        
        logger.info(f"批量解析: 总数 {len(links)}, 成功 {len(nodes)}")
        return nodes

