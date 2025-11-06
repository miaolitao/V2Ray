"""V2Ray 节点聚合系统核心模块"""

__version__ = "1.0.0"
__author__ = "V2Ray Team"

from .parser import NodeParser
from .collector import NodeCollector
from .deduplicator import Deduplicator
from .formatter import Formatter
from .config_manager import ConfigManager

__all__ = [
    'NodeParser',
    'NodeCollector',
    'Deduplicator',
    'Formatter',
    'ConfigManager',
]

