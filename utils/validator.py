"""节点验证工具"""

import re
from typing import Optional
from urllib.parse import urlparse


def validate_url(url: str) -> bool:
    """
    验证 URL 格式
    
    Args:
        url: 待验证的 URL
    
    Returns:
        是否有效
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_ip(ip: str) -> bool:
    """
    验证 IP 地址格式
    
    Args:
        ip: IP 地址
    
    Returns:
        是否有效
    """
    # IPv4
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(ipv4_pattern, ip):
        parts = ip.split('.')
        return all(0 <= int(part) <= 255 for part in parts)
    
    # IPv6
    ipv6_pattern = r'^([0-9a-fA-F]{0,4}:){7}[0-9a-fA-F]{0,4}$'
    if re.match(ipv6_pattern, ip):
        return True
    
    return False


def validate_domain(domain: str) -> bool:
    """
    验证域名格式
    
    Args:
        domain: 域名
    
    Returns:
        是否有效
    """
    domain_pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    return bool(re.match(domain_pattern, domain))


def validate_port(port: int) -> bool:
    """
    验证端口号
    
    Args:
        port: 端口号
    
    Returns:
        是否有效
    """
    return 1 <= port <= 65535


def validate_node(node_data: dict) -> bool:
    """
    验证节点数据的完整性
    
    Args:
        node_data: 节点数据字典
    
    Returns:
        是否有效
    """
    required_fields = ['protocol', 'server', 'port']
    
    # 检查必需字段
    for field in required_fields:
        if field not in node_data or not node_data[field]:
            return False
    
    # 验证服务器地址
    server = node_data['server']
    if not (validate_ip(server) or validate_domain(server)):
        return False
    
    # 验证端口
    try:
        port = int(node_data['port'])
        if not validate_port(port):
            return False
    except (ValueError, TypeError):
        return False
    
    # 验证协议
    valid_protocols = ['ss', 'ssr', 'vmess', 'trojan', 'vless']
    if node_data['protocol'].lower() not in valid_protocols:
        return False
    
    return True


def sanitize_name(name: str) -> str:
    """
    清理节点名称
    
    Args:
        name: 原始名称
    
    Returns:
        清理后的名称
    """
    # 移除特殊字符
    name = re.sub(r'[^\w\s\-\.\(\)\[\]【】]', '', name)
    # 限制长度
    if len(name) > 50:
        name = name[:50]
    return name.strip() or "未命名节点"

