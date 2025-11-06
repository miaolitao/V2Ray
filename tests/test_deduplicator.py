"""去重模块测试"""

import pytest
from src.parser import Node
from src.deduplicator import Deduplicator


class TestDeduplicator:
    """Deduplicator 测试类"""
    
    def test_remove_duplicates_by_hash(self):
        """测试基于哈希的去重"""
        nodes = [
            Node(protocol="ss", server="1.1.1.1", port=443, password="pass1", method="aes-256-gcm", name="Node1"),
            Node(protocol="ss", server="1.1.1.1", port=443, password="pass1", method="aes-256-gcm", name="Node2"),  # 重复
            Node(protocol="ss", server="2.2.2.2", port=443, password="pass2", method="aes-256-gcm", name="Node3"),
        ]
        
        dedup = Deduplicator(method="hash")
        unique_nodes = dedup.remove_duplicates(nodes)
        
        assert len(unique_nodes) == 2
    
    def test_remove_duplicates_by_address(self):
        """测试基于地址的去重"""
        nodes = [
            Node(protocol="ss", server="1.1.1.1", port=443, password="pass1", method="aes-256-gcm", name="Node1"),
            Node(protocol="ss", server="1.1.1.1", port=443, password="pass2", method="aes-256-gcm", name="Node2"),  # 同地址
            Node(protocol="ss", server="2.2.2.2", port=443, password="pass3", method="aes-256-gcm", name="Node3"),
        ]
        
        dedup = Deduplicator(method="address")
        unique_nodes = dedup.remove_duplicates(nodes)
        
        assert len(unique_nodes) == 2
    
    def test_group_by_protocol(self):
        """测试按协议分组"""
        nodes = [
            Node(protocol="ss", server="1.1.1.1", port=443, password="pass1", method="aes-256-gcm", name="SS1"),
            Node(protocol="ss", server="2.2.2.2", port=443, password="pass2", method="aes-256-gcm", name="SS2"),
            Node(protocol="vmess", server="3.3.3.3", port=443, password="uuid1", name="VMess1"),
        ]
        
        dedup = Deduplicator()
        grouped = dedup.group_by_protocol(nodes)
        
        assert len(grouped) == 2
        assert len(grouped["ss"]) == 2
        assert len(grouped["vmess"]) == 1
    
    def test_filter_by_keywords(self):
        """测试关键词过滤"""
        nodes = [
            Node(protocol="ss", server="1.1.1.1", port=443, password="pass1", method="aes-256-gcm", name="优质节点"),
            Node(protocol="ss", server="2.2.2.2", port=443, password="pass2", method="aes-256-gcm", name="过期节点"),
            Node(protocol="ss", server="3.3.3.3", port=443, password="pass3", method="aes-256-gcm", name="正常节点"),
        ]
        
        dedup = Deduplicator()
        filtered = dedup.filter_by_keywords(nodes, exclude_keywords=["过期"])
        
        assert len(filtered) == 2
        assert all("过期" not in n.name for n in filtered)
    
    def test_limit_nodes_per_protocol(self):
        """测试限制每种协议的节点数"""
        nodes = [
            Node(protocol="ss", server=f"{i}.{i}.{i}.{i}", port=443, password="pass", method="aes-256-gcm", name=f"SS{i}")
            for i in range(1, 6)
        ]
        
        dedup = Deduplicator()
        limited = dedup.limit_nodes_per_protocol(nodes, max_per_protocol=3)
        
        assert len(limited) == 3

