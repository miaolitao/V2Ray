"""配置管理模块"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from utils.logger import get_logger

logger = get_logger()


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: str = "config"):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置文件目录
        """
        self.config_dir = Path(config_dir)
        self.settings: Dict[str, Any] = {}
        self.sources: Dict[str, Any] = {}
        self.clash_template: Dict[str, Any] = {}
        
        self._load_configs()
    
    def _load_configs(self):
        """加载所有配置文件"""
        try:
            # 加载系统配置
            settings_file = self.config_dir / "settings.yaml"
            if settings_file.exists():
                with open(settings_file, 'r', encoding='utf-8') as f:
                    self.settings = yaml.safe_load(f) or {}
                logger.info(f"已加载系统配置: {settings_file}")
            else:
                logger.warning(f"系统配置文件不存在: {settings_file}")
            
            # 加载节点源配置
            sources_file = self.config_dir / "sources.yaml"
            if sources_file.exists():
                with open(sources_file, 'r', encoding='utf-8') as f:
                    self.sources = yaml.safe_load(f) or {}
                logger.info(f"已加载节点源配置: {sources_file}")
            else:
                logger.warning(f"节点源配置文件不存在: {sources_file}")
            
            # 加载 Clash 模板
            clash_file = self.config_dir / "clash_template.yaml"
            if clash_file.exists():
                with open(clash_file, 'r', encoding='utf-8') as f:
                    self.clash_template = yaml.safe_load(f) or {}
                logger.info(f"已加载 Clash 模板: {clash_file}")
            else:
                logger.warning(f"Clash 模板文件不存在: {clash_file}")
        
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            raise
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            key: 配置键（支持点号分隔的嵌套键）
            default: 默认值
        
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.settings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_sources(self, source_type: Optional[str] = None) -> list:
        """
        获取节点源列表
        
        Args:
            source_type: 源类型（subscription_sources, github_sources, telegram_sources）
        
        Returns:
            节点源列表
        """
        if source_type:
            sources = self.sources.get(source_type, [])
        else:
            sources = []
            for key in ['subscription_sources', 'github_sources', 'telegram_sources']:
                sources.extend(self.sources.get(key, []))
        
        # 只返回启用的源
        return [s for s in sources if s.get('enabled', True)]
    
    def get_clash_template(self) -> Dict[str, Any]:
        """
        获取 Clash 模板
        
        Returns:
            Clash 模板字典
        """
        return self.clash_template.copy()
    
    def save_config(self, config_type: str, data: Dict[str, Any]):
        """
        保存配置
        
        Args:
            config_type: 配置类型（settings, sources, clash_template）
            data: 配置数据
        """
        file_map = {
            'settings': 'settings.yaml',
            'sources': 'sources.yaml',
            'clash_template': 'clash_template.yaml'
        }
        
        if config_type not in file_map:
            raise ValueError(f"未知的配置类型: {config_type}")
        
        config_file = self.config_dir / file_map[config_type]
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
            logger.info(f"配置已保存: {config_file}")
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            raise

