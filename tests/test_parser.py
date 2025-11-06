"""节点解析器测试"""

import pytest
from src.parser import NodeParser, Node


class TestNodeParser:
    """NodeParser 测试类"""
    
    def test_parse_ss_link(self):
        """测试 SS 链接解析"""
        link = "ss://YWVzLTI1Ni1nY206dGVzdHBhc3N3b3JkQDEyNy4wLjAuMTo4MDgw#TestSS"
        node = NodeParser.parse(link)
        
        assert node is not None
        assert node.protocol == "ss"
        assert node.server == "127.0.0.1"
        assert node.port == 8080
        assert "TestSS" in node.name
    
    def test_parse_vmess_link(self):
        """测试 VMess 链接解析"""
        import base64
        import json
        
        config = {
            "v": "2",
            "ps": "TestVMess",
            "add": "127.0.0.1",
            "port": "443",
            "id": "12345678-1234-1234-1234-123456789012",
            "aid": "0",
            "net": "tcp",
            "type": "none",
            "tls": ""
        }
        
        json_str = json.dumps(config)
        encoded = base64.b64encode(json_str.encode()).decode()
        link = f"vmess://{encoded}"
        
        node = NodeParser.parse(link)
        
        assert node is not None
        assert node.protocol == "vmess"
        assert node.server == "127.0.0.1"
        assert node.port == 443
        assert node.name == "TestVMess"
    
    def test_parse_trojan_link(self):
        """测试 Trojan 链接解析"""
        link = "trojan://password123@example.com:443?sni=example.com#TestTrojan"
        node = NodeParser.parse(link)
        
        assert node is not None
        assert node.protocol == "trojan"
        assert node.server == "example.com"
        assert node.port == 443
        assert node.password == "password123"
        assert "TestTrojan" in node.name
    
    def test_parse_vless_link(self):
        """测试 VLESS 链接解析"""
        link = "vless://12345678-1234-1234-1234-123456789012@example.com:443?encryption=none#TestVLESS"
        node = NodeParser.parse(link)
        
        assert node is not None
        assert node.protocol == "vless"
        assert node.server == "example.com"
        assert node.port == 443
        assert "TestVLESS" in node.name
    
    def test_parse_invalid_link(self):
        """测试无效链接"""
        link = "invalid://link"
        node = NodeParser.parse(link)
        
        assert node is None
    
    def test_parse_batch(self):
        """测试批量解析"""
        links = [
            "ss://YWVzLTI1Ni1nY206dGVzdEAxMjcuMC4wLjE6ODA4MA==#SS1",
            "trojan://pass@example.com:443#Trojan1",
            "invalid://link",
        ]
        
        nodes = NodeParser.parse_batch(links)
        
        assert len(nodes) == 2  # 只有两个有效
        assert nodes[0].protocol in ["ss", "trojan"]
        assert nodes[1].protocol in ["ss", "trojan"]

