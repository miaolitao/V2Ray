"""去重模块 - 移除重复节点"""

import hashlib
from typing import List, Dict, Set
from collections import defaultdict
from .parser import Node
from utils.logger import get_logger

logger = get_logger()


class Deduplicator:
    """节点去重器"""
    
    def __init__(self, method: str = "hash", keep_faster: bool = True):
        """
        初始化去重器
        
        Args:
            method: 去重方式（hash, address, both）
            keep_faster: 是否保留速度更快的重复节点
        """
        self.method = method
        self.keep_faster = keep_faster
    
    def remove_duplicates(
        self,
        nodes: List[Node],
        speed_results: Dict[str, float] = None
    ) -> List[Node]:
        """
        移除重复节点
        
        Args:
            nodes: 节点列表
            speed_results: 速度测试结果（节点哈希 -> 速度）
        
        Returns:
            去重后的节点列表
        """
        if not nodes:
            return []
        
        logger.info(f"开始去重，原始节点数: {len(nodes)}")
        
        if self.method == "hash":
            unique_nodes = self._deduplicate_by_hash(nodes, speed_results)
        elif self.method == "address":
            unique_nodes = self._deduplicate_by_address(nodes, speed_results)
        elif self.method == "both":
            # 先按哈希去重，再按地址去重
            temp_nodes = self._deduplicate_by_hash(nodes, speed_results)
            unique_nodes = self._deduplicate_by_address(temp_nodes, speed_results)
        else:
            logger.warning(f"未知的去重方式: {self.method}，使用默认方式（hash）")
            unique_nodes = self._deduplicate_by_hash(nodes, speed_results)
        
        removed_count = len(nodes) - len(unique_nodes)
        logger.info(f"去重完成，移除 {removed_count} 个重复节点，剩余 {len(unique_nodes)} 个节点")
        
        return unique_nodes
    
    def _deduplicate_by_hash(
        self,
        nodes: List[Node],
        speed_results: Dict[str, float] = None
    ) -> List[Node]:
        """
        基于配置哈希去重
        
        Args:
            nodes: 节点列表
            speed_results: 速度测试结果
        
        Returns:
            去重后的节点列表
        """
        seen_hashes: Dict[str, Node] = {}
        
        for node in nodes:
            node_hash = self._calculate_hash(node)
            
            if node_hash not in seen_hashes:
                seen_hashes[node_hash] = node
            else:
                # 如果启用保留更快节点，比较速度
                if self.keep_faster and speed_results:
                    existing_node = seen_hashes[node_hash]
                    existing_speed = speed_results.get(
                        self._calculate_hash(existing_node),
                        0
                    )
                    current_speed = speed_results.get(node_hash, 0)
                    
                    if current_speed > existing_speed:
                        seen_hashes[node_hash] = node
        
        return list(seen_hashes.values())
    
    def _deduplicate_by_address(
        self,
        nodes: List[Node],
        speed_results: Dict[str, float] = None
    ) -> List[Node]:
        """
        基于服务器地址和端口去重
        
        Args:
            nodes: 节点列表
            speed_results: 速度测试结果
        
        Returns:
            去重后的节点列表
        """
        seen_addresses: Dict[str, Node] = {}
        
        for node in nodes:
            address_key = f"{node.server}:{node.port}"
            
            if address_key not in seen_addresses:
                seen_addresses[address_key] = node
            else:
                # 如果启用保留更快节点，比较速度
                if self.keep_faster and speed_results:
                    existing_node = seen_addresses[address_key]
                    existing_speed = speed_results.get(
                        self._calculate_hash(existing_node),
                        0
                    )
                    current_speed = speed_results.get(
                        self._calculate_hash(node),
                        0
                    )
                    
                    if current_speed > existing_speed:
                        seen_addresses[address_key] = node
        
        return list(seen_addresses.values())
    
    def _calculate_hash(self, node: Node) -> str:
        """
        计算节点哈希值
        
        Args:
            node: 节点对象
        
        Returns:
            哈希值字符串
        """
        # 使用关键配置生成哈希
        hash_components = [
            node.protocol,
            node.server,
            str(node.port),
            node.password,
            node.method,
        ]
        
        # 添加协议特定参数
        if node.extra:
            for key in sorted(node.extra.keys()):
                value = node.extra[key]
                if value:  # 只包含非空值
                    hash_components.append(f"{key}={value}")
        
        hash_string = "|".join(hash_components)
        return hashlib.md5(hash_string.encode('utf-8')).hexdigest()
    
    def group_by_protocol(self, nodes: List[Node]) -> Dict[str, List[Node]]:
        """
        按协议分组节点
        
        Args:
            nodes: 节点列表
        
        Returns:
            协议 -> 节点列表的字典
        """
        grouped: Dict[str, List[Node]] = defaultdict(list)
        
        for node in nodes:
            grouped[node.protocol].append(node)
        
        return dict(grouped)
    
    def limit_nodes_per_protocol(
        self,
        nodes: List[Node],
        max_per_protocol: int
    ) -> List[Node]:
        """
        限制每种协议的节点数量
        
        Args:
            nodes: 节点列表
            max_per_protocol: 每种协议的最大节点数
        
        Returns:
            限制后的节点列表
        """
        grouped = self.group_by_protocol(nodes)
        limited_nodes = []
        
        for protocol, protocol_nodes in grouped.items():
            if len(protocol_nodes) > max_per_protocol:
                logger.info(
                    f"协议 {protocol} 节点数 {len(protocol_nodes)} "
                    f"超过限制 {max_per_protocol}，进行裁剪"
                )
                protocol_nodes = protocol_nodes[:max_per_protocol]
            
            limited_nodes.extend(protocol_nodes)
        
        return limited_nodes
    
    def filter_by_keywords(
        self,
        nodes: List[Node],
        exclude_keywords: List[str] = None,
        include_keywords: List[str] = None
    ) -> List[Node]:
        """
        根据关键词过滤节点
        
        Args:
            nodes: 节点列表
            exclude_keywords: 排除关键词列表
            include_keywords: 包含关键词列表
        
        Returns:
            过滤后的节点列表
        """
        filtered_nodes = []
        
        for node in nodes:
            node_text = f"{node.name} {node.server}".lower()
            
            # 检查排除关键词
            if exclude_keywords:
                should_exclude = False
                for keyword in exclude_keywords:
                    if keyword.lower() in node_text:
                        should_exclude = True
                        break
                if should_exclude:
                    continue
            
            # 检查包含关键词
            if include_keywords:
                should_include = False
                for keyword in include_keywords:
                    if keyword.lower() in node_text:
                        should_include = True
                        break
                if not should_include:
                    continue
            
            filtered_nodes.append(node)
        
        removed = len(nodes) - len(filtered_nodes)
        if removed > 0:
            logger.info(f"关键词过滤移除 {removed} 个节点")
        
        return filtered_nodes

