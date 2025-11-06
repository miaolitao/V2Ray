"""格式转换器测试"""

import pytest
import base64
import yaml
import json
from src.parser import Node
from src.formatter import Formatter


class TestFormatter:
    """Formatter 测试类"""
    
    @pytest.fixture
    def sample_nodes(self):
        """示例节点"""
        return [
            Node(
                protocol="ss",
                server="1.1.1.1",
                port=443,
                password="password123",
                method="aes-256-gcm",
                name="SS节点1"
            ),
            Node(
                protocol="vmess",
                server="2.2.2.2",
                port=443,
                password="12345678-1234-1234-1234-123456789012",
                method="auto",
                name="VMess节点1",
                extra={"aid": 0, "net": "tcp", "tls": ""}
            ),
        ]
    
    def test_to_base64(self, sample_nodes):
        """测试 Base64 格式转换"""
        formatter = Formatter()
        result = formatter.to_base64(sample_nodes)
        
        assert result is not None
        assert len(result) > 0
        
        # 解码验证
        decoded = base64.b64decode(result).decode('utf-8')
        assert "ss://" in decoded or "vmess://" in decoded
    
    def test_to_clash_yaml(self, sample_nodes):
        """测试 Clash YAML 格式转换"""
        formatter = Formatter()
        result = formatter.to_clash_yaml(sample_nodes)
        
        assert result is not None
        
        # 解析 YAML 验证
        config = yaml.safe_load(result)
        assert "proxies" in config
        assert len(config["proxies"]) == 2
        assert config["proxies"][0]["type"] in ["ss", "vmess"]
    
    def test_to_v2ray_json(self, sample_nodes):
        """测试 V2Ray JSON 格式转换"""
        formatter = Formatter()
        result = formatter.to_v2ray_json(sample_nodes)
        
        assert result is not None
        
        # 解析 JSON 验证
        config = json.loads(result)
        assert "outbounds" in config
        assert len(config["outbounds"]) == 2
    
    def test_to_surge(self, sample_nodes):
        """测试 Surge 格式转换"""
        formatter = Formatter()
        result = formatter.to_surge(sample_nodes)
        
        assert result is not None
        assert "[Proxy]" in result
        assert "SS节点1" in result or "VMess节点1" in result
    
    def test_to_quantumult(self, sample_nodes):
        """测试 Quantumult X 格式转换"""
        formatter = Formatter()
        result = formatter.to_quantumult(sample_nodes)
        
        assert result is not None
        assert "[server_local]" in result
    
    def test_node_to_ss_link(self, sample_nodes):
        """测试节点转 SS 链接"""
        formatter = Formatter()
        ss_node = sample_nodes[0]
        
        link = formatter._node_to_link(ss_node)
        
        assert link.startswith("ss://")
        assert "#" in link  # 包含名称
    
    def test_node_to_vmess_link(self, sample_nodes):
        """测试节点转 VMess 链接"""
        formatter = Formatter()
        vmess_node = sample_nodes[1]
        
        link = formatter._node_to_link(vmess_node)
        
        assert link.startswith("vmess://")

