"""测速模块 - 测试节点速度和可用性"""

import asyncio
import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import aiohttp
from .parser import Node
from utils.logger import get_logger

logger = get_logger()


@dataclass
class TestResult:
    """测速结果"""
    node: Node
    available: bool = False
    latency: float = 0.0  # 毫秒
    speed: float = 0.0  # MB/s
    error: str = ""
    
    def __repr__(self):
        if self.available:
            return f"<TestResult {self.node.name}: {self.latency:.2f}ms, {self.speed:.2f}MB/s>"
        else:
            return f"<TestResult {self.node.name}: 不可用 - {self.error}>"


class SpeedTester:
    """节点测速器"""
    
    def __init__(self, config_manager=None):
        """
        初始化测速器
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config = config_manager
        
        # 从配置获取参数
        if config_manager:
            self.enabled = config_manager.get_setting('speed_test.enabled', True)
            self.timeout = config_manager.get_setting('speed_test.timeout', 15)
            self.min_speed = config_manager.get_setting('speed_test.min_speed', 1.0)
            self.max_latency = config_manager.get_setting('speed_test.max_latency', 1000)
            self.test_url = config_manager.get_setting(
                'speed_test.test_url',
                'https://www.google.com/generate_204'
            )
            self.concurrent_tests = config_manager.get_setting('speed_test.concurrent_tests', 50)
        else:
            self.enabled = True
            self.timeout = 15
            self.min_speed = 1.0
            self.max_latency = 1000
            self.test_url = 'https://www.google.com/generate_204'
            self.concurrent_tests = 50
    
    async def test_all(self, nodes: List[Node]) -> List[TestResult]:
        """
        测试所有节点
        
        Args:
            nodes: 节点列表
        
        Returns:
            测速结果列表
        """
        if not self.enabled:
            logger.info("测速功能已禁用")
            return [TestResult(node=node) for node in nodes]
        
        logger.info(f"开始测试 {len(nodes)} 个节点的速度...")
        
        # 分批测试以控制并发数
        results = []
        for i in range(0, len(nodes), self.concurrent_tests):
            batch = nodes[i:i + self.concurrent_tests]
            batch_results = await self._test_batch(batch)
            results.extend(batch_results)
            
            logger.info(f"已测试 {min(i + self.concurrent_tests, len(nodes))}/{len(nodes)} 个节点")
        
        # 统计结果
        available_count = sum(1 for r in results if r.available)
        logger.info(f"测速完成，可用节点: {available_count}/{len(nodes)}")
        
        return results
    
    async def _test_batch(self, nodes: List[Node]) -> List[TestResult]:
        """
        批量测试节点
        
        Args:
            nodes: 节点列表
        
        Returns:
            测速结果列表
        """
        tasks = [self.test_node(node) for node in nodes]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.debug(f"节点测试异常: {nodes[i].name}, 错误: {result}")
                processed_results.append(
                    TestResult(node=nodes[i], available=False, error=str(result))
                )
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def test_node(self, node: Node) -> TestResult:
        """
        测试单个节点
        
        由于直接测试代理节点需要代理客户端支持，这里使用简化方式：
        - 测试连通性（TCP 连接）
        - 估算延迟
        
        实际生产环境建议集成 LiteSpeedTest 等专业工具
        
        Args:
            node: 节点对象
        
        Returns:
            测速结果
        """
        result = TestResult(node=node)
        
        try:
            # 测试 TCP 连接和延迟
            latency = await self._test_latency(node.server, node.port)
            
            if latency > 0:
                result.available = True
                result.latency = latency
                # 这里简化处理，实际应该通过代理测试下载速度
                # 根据延迟估算一个速度值（仅供排序参考）
                result.speed = self._estimate_speed(latency)
            else:
                result.available = False
                result.error = "连接失败"
        
        except asyncio.TimeoutError:
            result.available = False
            result.error = "连接超时"
        except Exception as e:
            result.available = False
            result.error = str(e)
        
        return result
    
    async def _test_latency(self, host: str, port: int) -> float:
        """
        测试延迟（TCP 连接时间）
        
        Args:
            host: 主机地址
            port: 端口
        
        Returns:
            延迟（毫秒），失败返回 0
        """
        try:
            start_time = time.time()
            
            # 尝试建立 TCP 连接
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=self.timeout
            )
            
            end_time = time.time()
            latency = (end_time - start_time) * 1000  # 转换为毫秒
            
            writer.close()
            await writer.wait_closed()
            
            return latency
        
        except Exception as e:
            logger.debug(f"延迟测试失败 {host}:{port}, 错误: {e}")
            return 0.0
    
    def _estimate_speed(self, latency: float) -> float:
        """
        根据延迟估算速度（仅供参考）
        
        实际应该通过代理下载测试文件来测量真实速度
        这里使用一个简单的公式来估算
        
        Args:
            latency: 延迟（毫秒）
        
        Returns:
            估算速度（MB/s）
        """
        # 简单的反比关系：延迟越低，速度越快
        if latency < 50:
            return 10.0
        elif latency < 100:
            return 8.0
        elif latency < 200:
            return 5.0
        elif latency < 300:
            return 3.0
        elif latency < 500:
            return 2.0
        else:
            return 1.0
    
    def filter_by_test_results(
        self,
        results: List[TestResult],
        filter_invalid: bool = True
    ) -> List[TestResult]:
        """
        根据测试结果过滤节点
        
        Args:
            results: 测试结果列表
            filter_invalid: 是否过滤不可用节点
        
        Returns:
            过滤后的结果列表
        """
        filtered = results
        
        if filter_invalid:
            filtered = [r for r in filtered if r.available]
        
        # 按速度要求过滤
        filtered = [
            r for r in filtered
            if r.speed >= self.min_speed
        ]
        
        # 按延迟要求过滤
        filtered = [
            r for r in filtered
            if r.latency <= self.max_latency
        ]
        
        removed = len(results) - len(filtered)
        if removed > 0:
            logger.info(f"根据测速结果过滤，移除 {removed} 个节点")
        
        return filtered
    
    def sort_results(
        self,
        results: List[TestResult],
        sort_by: str = "speed"
    ) -> List[TestResult]:
        """
        排序测试结果
        
        Args:
            results: 测试结果列表
            sort_by: 排序方式（speed, latency）
        
        Returns:
            排序后的结果列表
        """
        if sort_by == "speed":
            # 按速度降序
            sorted_results = sorted(
                results,
                key=lambda r: r.speed if r.available else -1,
                reverse=True
            )
        elif sort_by == "latency":
            # 按延迟升序
            sorted_results = sorted(
                results,
                key=lambda r: r.latency if r.available else float('inf')
            )
        else:
            logger.warning(f"未知的排序方式: {sort_by}，使用默认排序（速度）")
            sorted_results = sorted(
                results,
                key=lambda r: r.speed if r.available else -1,
                reverse=True
            )
        
        return sorted_results
    
    def get_speed_dict(self, results: List[TestResult]) -> Dict[str, float]:
        """
        获取节点哈希 -> 速度的字典（用于去重时选择更快节点）
        
        Args:
            results: 测试结果列表
        
        Returns:
            节点哈希 -> 速度的字典
        """
        import hashlib
        
        speed_dict = {}
        for result in results:
            if result.available:
                # 使用简单的节点标识
                node_id = f"{result.node.server}:{result.node.port}"
                speed_dict[node_id] = result.speed
        
        return speed_dict

