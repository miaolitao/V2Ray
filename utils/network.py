"""网络工具模块"""

import asyncio
from typing import Optional, Dict, Any
import aiohttp
import requests
from .logger import get_logger

logger = get_logger()


async def fetch_url(
    url: str,
    timeout: int = 10,
    headers: Optional[Dict[str, str]] = None,
    retry: int = 3
) -> Optional[str]:
    """
    异步获取 URL 内容
    
    Args:
        url: 目标 URL
        timeout: 超时时间（秒）
        headers: 自定义请求头
        retry: 重试次数
    
    Returns:
        URL 内容，失败返回 None
    """
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    for attempt in range(retry):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as response:
                    if response.status == 200:
                        content = await response.text()
                        logger.debug(f"成功获取 URL: {url}")
                        return content
                    else:
                        logger.warning(f"URL 返回状态码 {response.status}: {url}")
        except asyncio.TimeoutError:
            logger.warning(f"URL 请求超时 (尝试 {attempt + 1}/{retry}): {url}")
        except Exception as e:
            logger.warning(f"URL 请求失败 (尝试 {attempt + 1}/{retry}): {url}, 错误: {e}")
        
        if attempt < retry - 1:
            await asyncio.sleep(1)
    
    logger.error(f"URL 获取失败（已重试 {retry} 次）: {url}")
    return None


def fetch_content(
    url: str,
    timeout: int = 10,
    headers: Optional[Dict[str, str]] = None
) -> Optional[str]:
    """
    同步获取 URL 内容
    
    Args:
        url: 目标 URL
        timeout: 超时时间（秒）
        headers: 自定义请求头
    
    Returns:
        URL 内容，失败返回 None
    """
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        if response.status_code == 200:
            return response.text
        else:
            logger.warning(f"URL 返回状态码 {response.status_code}: {url}")
    except Exception as e:
        logger.error(f"URL 请求失败: {url}, 错误: {e}")
    
    return None


async def test_connectivity(
    url: str,
    timeout: int = 5
) -> bool:
    """
    测试 URL 连通性
    
    Args:
        url: 测试 URL
        timeout: 超时时间（秒）
    
    Returns:
        是否连通
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                return response.status in [200, 204]
    except Exception:
        return False

