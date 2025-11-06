"""格式转换器模块 - 将节点转换为各种客户端格式"""

import base64
import json
import yaml
from typing import List, Dict, Any, Optional
from pathlib import Path
from .parser import Node
from utils.logger import get_logger

logger = get_logger()


class Formatter:
    """格式转换器 - 支持多种输出格式"""
    
    def __init__(self, config_manager=None):
        """
        初始化格式转换器
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config = config_manager
    
    def to_base64(self, nodes: List[Node]) -> str:
        """
        转换为 Base64 格式（通用订阅格式）
        
        Args:
            nodes: 节点列表
        
        Returns:
            Base64 编码的节点链接
        """
        links = []
        
        for node in nodes:
            link = self._node_to_link(node)
            if link:
                links.append(link)
        
        # 将所有链接合并并编码
        content = '\n'.join(links)
        encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        logger.info(f"生成 Base64 格式，包含 {len(links)} 个节点")
        return encoded
    
    def _node_to_link(self, node: Node) -> str:
        """
        将节点对象转换为链接格式
        
        Args:
            node: 节点对象
        
        Returns:
            节点链接
        """
        if node.protocol == 'ss':
            return self._node_to_ss_link(node)
        elif node.protocol == 'ssr':
            return self._node_to_ssr_link(node)
        elif node.protocol == 'vmess':
            return self._node_to_vmess_link(node)
        elif node.protocol == 'trojan':
            return self._node_to_trojan_link(node)
        elif node.protocol == 'vless':
            return self._node_to_vless_link(node)
        else:
            logger.warning(f"不支持的协议: {node.protocol}")
            return ""
    
    def _node_to_ss_link(self, node: Node) -> str:
        """生成 SS 链接"""
        # 格式: ss://base64(method:password@server:port)#name
        auth = f"{node.method}:{node.password}@{node.server}:{node.port}"
        encoded_auth = base64.urlsafe_b64encode(auth.encode('utf-8')).decode('utf-8').rstrip('=')
        
        from urllib.parse import quote
        name = quote(node.name)
        
        return f"ss://{encoded_auth}#{name}"
    
    def _node_to_ssr_link(self, node: Node) -> str:
        """生成 SSR 链接"""
        # 格式: ssr://base64(server:port:protocol:method:obfs:base64pass/?params)
        protocol = node.extra.get('protocol', 'origin')
        obfs = node.extra.get('obfs', 'plain')
        
        password_b64 = base64.urlsafe_b64encode(
            node.password.encode('utf-8')
        ).decode('utf-8').rstrip('=')
        
        main = f"{node.server}:{node.port}:{protocol}:{node.method}:{obfs}:{password_b64}"
        
        # 添加参数
        params = []
        if node.extra.get('obfs_param'):
            obfsparam = base64.urlsafe_b64encode(
                node.extra['obfs_param'].encode('utf-8')
            ).decode('utf-8').rstrip('=')
            params.append(f"obfsparam={obfsparam}")
        
        if node.extra.get('protocol_param'):
            protoparam = base64.urlsafe_b64encode(
                node.extra['protocol_param'].encode('utf-8')
            ).decode('utf-8').rstrip('=')
            params.append(f"protoparam={protoparam}")
        
        remarks = base64.urlsafe_b64encode(node.name.encode('utf-8')).decode('utf-8').rstrip('=')
        params.append(f"remarks={remarks}")
        
        if params:
            main += "/?" + "&".join(params)
        
        encoded = base64.urlsafe_b64encode(main.encode('utf-8')).decode('utf-8').rstrip('=')
        return f"ssr://{encoded}"
    
    def _node_to_vmess_link(self, node: Node) -> str:
        """生成 VMess 链接"""
        # 格式: vmess://base64(json)
        config = {
            "v": "2",
            "ps": node.name,
            "add": node.server,
            "port": str(node.port),
            "id": node.password,
            "aid": str(node.extra.get('aid', 0)),
            "scy": node.method or "auto",
            "net": node.extra.get('net', 'tcp'),
            "type": node.extra.get('type', 'none'),
            "host": node.extra.get('host', ''),
            "path": node.extra.get('path', ''),
            "tls": node.extra.get('tls', ''),
            "sni": node.extra.get('sni', ''),
            "alpn": node.extra.get('alpn', ''),
        }
        
        json_str = json.dumps(config, separators=(',', ':'))
        encoded = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
        
        return f"vmess://{encoded}"
    
    def _node_to_trojan_link(self, node: Node) -> str:
        """生成 Trojan 链接"""
        # 格式: trojan://password@server:port?params#name
        from urllib.parse import quote, urlencode
        
        link = f"trojan://{node.password}@{node.server}:{node.port}"
        
        # 添加参数
        params = {}
        if node.extra.get('sni'):
            params['sni'] = node.extra['sni']
        if node.extra.get('type'):
            params['type'] = node.extra['type']
        if node.extra.get('security'):
            params['security'] = node.extra['security']
        if node.extra.get('skip_cert_verify'):
            params['allowInsecure'] = '1'
        
        if params:
            link += "?" + urlencode(params)
        
        link += "#" + quote(node.name)
        
        return link
    
    def _node_to_vless_link(self, node: Node) -> str:
        """生成 VLESS 链接"""
        # 格式: vless://uuid@server:port?params#name
        from urllib.parse import quote, urlencode
        
        link = f"vless://{node.password}@{node.server}:{node.port}"
        
        # 添加参数
        params = {}
        if node.method and node.method != 'none':
            params['encryption'] = node.method
        if node.extra.get('flow'):
            params['flow'] = node.extra['flow']
        if node.extra.get('type'):
            params['type'] = node.extra['type']
        if node.extra.get('security'):
            params['security'] = node.extra['security']
        if node.extra.get('sni'):
            params['sni'] = node.extra['sni']
        if node.extra.get('alpn'):
            params['alpn'] = node.extra['alpn']
        if node.extra.get('fp'):
            params['fp'] = node.extra['fp']
        
        if params:
            link += "?" + urlencode(params)
        
        link += "#" + quote(node.name)
        
        return link
    
    def to_clash_yaml(self, nodes: List[Node], template: Dict[str, Any] = None) -> str:
        """
        转换为 Clash YAML 格式
        
        Args:
            nodes: 节点列表
            template: Clash 配置模板
        
        Returns:
            Clash YAML 配置
        """
        if template is None and self.config:
            template = self.config.get_clash_template()
        
        if template is None:
            template = self._get_default_clash_template()
        
        # 转换节点为 Clash 代理格式
        proxies = []
        proxy_names = []
        
        for node in nodes:
            proxy = self._node_to_clash_proxy(node)
            if proxy:
                proxies.append(proxy)
                proxy_names.append(proxy['name'])
        
        # 更新模板
        config = template.copy()
        config['proxies'] = proxies
        
        # 更新代理组
        if 'proxy-groups' in config:
            for group in config['proxy-groups']:
                if group['name'] in ['♻️ 自动选择', '🔮 负载均衡']:
                    group['proxies'] = proxy_names
                elif group['name'] == '🚀 节点选择':
                    group['proxies'] = ['♻️ 自动选择', '🔮 负载均衡', 'DIRECT'] + proxy_names
        
        yaml_content = yaml.dump(
            config,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False
        )
        
        logger.info(f"生成 Clash 配置，包含 {len(proxies)} 个节点")
        return yaml_content
    
    def _node_to_clash_proxy(self, node: Node) -> Dict[str, Any]:
        """将节点转换为 Clash 代理格式"""
        if node.protocol == 'ss':
            return {
                'name': node.name,
                'type': 'ss',
                'server': node.server,
                'port': node.port,
                'cipher': node.method,
                'password': node.password,
            }
        
        elif node.protocol == 'ssr':
            return {
                'name': node.name,
                'type': 'ssr',
                'server': node.server,
                'port': node.port,
                'cipher': node.method,
                'password': node.password,
                'protocol': node.extra.get('protocol', 'origin'),
                'obfs': node.extra.get('obfs', 'plain'),
                'protocol-param': node.extra.get('protocol_param', ''),
                'obfs-param': node.extra.get('obfs_param', ''),
            }
        
        elif node.protocol == 'vmess':
            proxy = {
                'name': node.name,
                'type': 'vmess',
                'server': node.server,
                'port': node.port,
                'uuid': node.password,
                'alterId': node.extra.get('aid', 0),
                'cipher': node.method or 'auto',
            }
            
            # 网络类型
            net = node.extra.get('net', 'tcp')
            if net == 'ws':
                proxy['network'] = 'ws'
                proxy['ws-opts'] = {
                    'path': node.extra.get('path', '/'),
                    'headers': {
                        'Host': node.extra.get('host', '')
                    }
                }
            elif net == 'grpc':
                proxy['network'] = 'grpc'
                proxy['grpc-opts'] = {
                    'grpc-service-name': node.extra.get('path', '')
                }
            
            # TLS
            if node.extra.get('tls'):
                proxy['tls'] = True
                if node.extra.get('sni'):
                    proxy['servername'] = node.extra['sni']
            
            return proxy
        
        elif node.protocol == 'trojan':
            proxy = {
                'name': node.name,
                'type': 'trojan',
                'server': node.server,
                'port': node.port,
                'password': node.password,
            }
            
            if node.extra.get('sni'):
                proxy['sni'] = node.extra['sni']
            if node.extra.get('skip_cert_verify'):
                proxy['skip-cert-verify'] = True
            
            return proxy
        
        elif node.protocol == 'vless':
            proxy = {
                'name': node.name,
                'type': 'vless',
                'server': node.server,
                'port': node.port,
                'uuid': node.password,
            }
            
            if node.extra.get('flow'):
                proxy['flow'] = node.extra['flow']
            
            net = node.extra.get('type', 'tcp')
            if net != 'tcp':
                proxy['network'] = net
            
            security = node.extra.get('security', 'none')
            if security == 'tls':
                proxy['tls'] = True
                if node.extra.get('sni'):
                    proxy['servername'] = node.extra['sni']
            
            return proxy
        
        else:
            logger.warning(f"不支持转换为 Clash 格式的协议: {node.protocol}")
            return None
    
    def _get_default_clash_template(self) -> Dict[str, Any]:
        """获取默认 Clash 模板"""
        return {
            'port': 7890,
            'socks-port': 7891,
            'allow-lan': False,
            'mode': 'rule',
            'log-level': 'info',
            'external-controller': '127.0.0.1:9090',
            'proxies': [],
            'proxy-groups': [
                {
                    'name': '🚀 节点选择',
                    'type': 'select',
                    'proxies': ['DIRECT']
                }
            ],
            'rules': [
                'GEOIP,CN,DIRECT',
                'MATCH,🚀 节点选择'
            ]
        }
    
    def to_v2ray_json(self, nodes: List[Node]) -> str:
        """
        转换为 V2Ray JSON 格式
        
        Args:
            nodes: 节点列表
        
        Returns:
            V2Ray JSON 配置
        """
        outbounds = []
        
        for node in nodes:
            outbound = self._node_to_v2ray_outbound(node)
            if outbound:
                outbounds.append(outbound)
        
        config = {
            "log": {
                "loglevel": "warning"
            },
            "inbounds": [
                {
                    "port": 1080,
                    "protocol": "socks",
                    "settings": {
                        "auth": "noauth",
                        "udp": True
                    }
                },
                {
                    "port": 1081,
                    "protocol": "http"
                }
            ],
            "outbounds": outbounds,
            "routing": {
                "domainStrategy": "IPOnDemand",
                "rules": [
                    {
                        "type": "field",
                        "ip": ["geoip:private"],
                        "outboundTag": "direct"
                    },
                    {
                        "type": "field",
                        "ip": ["geoip:cn"],
                        "outboundTag": "direct"
                    }
                ]
            }
        }
        
        logger.info(f"生成 V2Ray JSON 配置，包含 {len(outbounds)} 个节点")
        return json.dumps(config, indent=2, ensure_ascii=False)
    
    def _node_to_v2ray_outbound(self, node: Node) -> Optional[Dict[str, Any]]:
        """将节点转换为 V2Ray outbound 格式"""
        
        if node.protocol == 'ss':
            return {
                "tag": node.name,
                "protocol": "shadowsocks",
                "settings": {
                    "servers": [
                        {
                            "address": node.server,
                            "port": node.port,
                            "method": node.method,
                            "password": node.password
                        }
                    ]
                }
            }
        
        elif node.protocol == 'vmess':
            return {
                "tag": node.name,
                "protocol": "vmess",
                "settings": {
                    "vnext": [
                        {
                            "address": node.server,
                            "port": node.port,
                            "users": [
                                {
                                    "id": node.password,
                                    "alterId": node.extra.get('aid', 0),
                                    "security": node.method or "auto"
                                }
                            ]
                        }
                    ]
                },
                "streamSettings": self._get_v2ray_stream_settings(node)
            }
        
        elif node.protocol == 'trojan':
            return {
                "tag": node.name,
                "protocol": "trojan",
                "settings": {
                    "servers": [
                        {
                            "address": node.server,
                            "port": node.port,
                            "password": node.password
                        }
                    ]
                },
                "streamSettings": {
                    "network": "tcp",
                    "security": "tls",
                    "tlsSettings": {
                        "serverName": node.extra.get('sni', ''),
                        "allowInsecure": node.extra.get('skip_cert_verify', False)
                    }
                }
            }
        
        elif node.protocol == 'vless':
            return {
                "tag": node.name,
                "protocol": "vless",
                "settings": {
                    "vnext": [
                        {
                            "address": node.server,
                            "port": node.port,
                            "users": [
                                {
                                    "id": node.password,
                                    "encryption": node.method or "none",
                                    "flow": node.extra.get('flow', '')
                                }
                            ]
                        }
                    ]
                },
                "streamSettings": self._get_v2ray_stream_settings(node)
            }
        
        else:
            logger.warning(f"不支持转换为 V2Ray 格式的协议: {node.protocol}")
            return None
    
    def _get_v2ray_stream_settings(self, node: Node) -> Dict[str, Any]:
        """获取 V2Ray streamSettings 配置"""
        settings = {
            "network": node.extra.get('net', 'tcp')
        }
        
        # WebSocket
        if settings['network'] == 'ws':
            settings['wsSettings'] = {
                "path": node.extra.get('path', '/'),
                "headers": {
                    "Host": node.extra.get('host', '')
                }
            }
        
        # gRPC
        elif settings['network'] == 'grpc':
            settings['grpcSettings'] = {
                "serviceName": node.extra.get('path', '')
            }
        
        # TLS
        if node.extra.get('tls'):
            settings['security'] = 'tls'
            settings['tlsSettings'] = {
                "serverName": node.extra.get('sni', ''),
                "allowInsecure": False
            }
        
        return settings
    
    def to_surge(self, nodes: List[Node]) -> str:
        """
        转换为 Surge 格式
        
        Args:
            nodes: 节点列表
        
        Returns:
            Surge 配置
        """
        config_lines = [
            "#!MANAGED-CONFIG",
            "",
            "[General]",
            "loglevel = notify",
            "skip-proxy = 127.0.0.1, 192.168.0.0/16, 10.0.0.0/8, 172.16.0.0/12, localhost, *.local",
            "",
            "[Proxy]",
        ]
        
        # 添加节点
        for node in nodes:
            line = self._node_to_surge_line(node)
            if line:
                config_lines.append(line)
        
        config_lines.extend([
            "",
            "[Proxy Group]",
            "Proxy = select, " + ", ".join([node.name for node in nodes]),
            "",
            "[Rule]",
            "GEOIP,CN,DIRECT",
            "FINAL,Proxy"
        ])
        
        content = "\n".join(config_lines)
        logger.info(f"生成 Surge 配置，包含 {len(nodes)} 个节点")
        return content
    
    def _node_to_surge_line(self, node: Node) -> str:
        """将节点转换为 Surge 配置行"""
        
        if node.protocol == 'ss':
            # 格式: ProxyName = ss, server, port, encrypt-method=method, password=password
            return f"{node.name} = ss, {node.server}, {node.port}, encrypt-method={node.method}, password={node.password}"
        
        elif node.protocol == 'vmess':
            # Surge 4+ 支持 VMess
            parts = [
                f"{node.name} = vmess",
                node.server,
                str(node.port),
                f"username={node.password}",
            ]
            
            if node.extra.get('tls'):
                parts.append("tls=true")
                if node.extra.get('sni'):
                    parts.append(f"sni={node.extra['sni']}")
            
            if node.extra.get('net') == 'ws':
                parts.append("ws=true")
                if node.extra.get('path'):
                    parts.append(f"ws-path={node.extra['path']}")
                if node.extra.get('host'):
                    parts.append(f"ws-headers=Host:{node.extra['host']}")
            
            return ", ".join(parts)
        
        elif node.protocol == 'trojan':
            # 格式: ProxyName = trojan, server, port, password=password
            parts = [
                f"{node.name} = trojan",
                node.server,
                str(node.port),
                f"password={node.password}",
            ]
            
            if node.extra.get('sni'):
                parts.append(f"sni={node.extra['sni']}")
            
            if node.extra.get('skip_cert_verify'):
                parts.append("skip-cert-verify=true")
            
            return ", ".join(parts)
        
        else:
            logger.debug(f"Surge 不支持的协议: {node.protocol}")
            return ""
    
    def to_quantumult(self, nodes: List[Node]) -> str:
        """
        转换为 Quantumult X 格式
        
        Args:
            nodes: 节点列表
        
        Returns:
            Quantumult X 配置
        """
        config_lines = [
            "[general]",
            "",
            "[server_local]",
        ]
        
        # 添加节点
        for node in nodes:
            line = self._node_to_quantumult_line(node)
            if line:
                config_lines.append(line)
        
        content = "\n".join(config_lines)
        logger.info(f"生成 Quantumult X 配置，包含 {len(nodes)} 个节点")
        return content
    
    def _node_to_quantumult_line(self, node: Node) -> str:
        """将节点转换为 Quantumult X 配置行"""
        
        if node.protocol == 'ss':
            # 格式: shadowsocks=server:port, method=method, password=password, tag=name
            return f"shadowsocks={node.server}:{node.port}, method={node.method}, password={node.password}, tag={node.name}"
        
        elif node.protocol == 'vmess':
            # 格式: vmess=server:port, method=method, password=uuid, tag=name
            parts = [
                f"vmess={node.server}:{node.port}",
                f"method={node.method or 'aes-128-gcm'}",
                f"password={node.password}",
            ]
            
            if node.extra.get('tls'):
                parts.append("obfs=over-tls")
                if node.extra.get('host'):
                    parts.append(f"obfs-host={node.extra['host']}")
            elif node.extra.get('net') == 'ws':
                parts.append("obfs=ws")
                if node.extra.get('host'):
                    parts.append(f"obfs-host={node.extra['host']}")
                if node.extra.get('path'):
                    parts.append(f"obfs-uri={node.extra['path']}")
            
            parts.append(f"tag={node.name}")
            
            return ", ".join(parts)
        
        elif node.protocol == 'trojan':
            # 格式: trojan=server:port, password=password, tag=name
            parts = [
                f"trojan={node.server}:{node.port}",
                f"password={node.password}",
            ]
            
            if node.extra.get('sni'):
                parts.append(f"obfs-host={node.extra['sni']}")
            
            parts.append(f"tag={node.name}")
            
            return ", ".join(parts)
        
        else:
            logger.debug(f"Quantumult X 不支持的协议: {node.protocol}")
            return ""
    
    def save_to_file(self, content: str, filepath: str):
        """
        保存内容到文件
        
        Args:
            content: 文件内容
            filepath: 文件路径
        """
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"已保存到文件: {filepath}")

