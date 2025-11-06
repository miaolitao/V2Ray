"""配置管理器测试"""

import pytest
import yaml
from pathlib import Path
from src.config_manager import ConfigManager


class TestConfigManager:
    """ConfigManager 测试类"""
    
    def test_init(self):
        """测试初始化"""
        config = ConfigManager()
        
        assert config is not None
        assert isinstance(config.settings, dict)
        assert isinstance(config.sources, dict)
    
    def test_get_setting(self):
        """测试获取配置"""
        config = ConfigManager()
        
        # 获取简单配置
        log_level = config.get_setting('general.log_level', 'INFO')
        assert log_level in ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        
        # 获取不存在的配置，应返回默认值
        result = config.get_setting('nonexistent.key', 'default_value')
        assert result == 'default_value'
    
    def test_get_sources(self):
        """测试获取节点源"""
        config = ConfigManager()
        
        # 获取所有源
        all_sources = config.get_sources()
        assert isinstance(all_sources, list)
        
        # 获取订阅源
        sub_sources = config.get_sources('subscription_sources')
        assert isinstance(sub_sources, list)
        
        # 验证启用的源
        for source in all_sources:
            assert 'name' in source
            assert source.get('enabled', True) is True
    
    def test_get_clash_template(self):
        """测试获取 Clash 模板"""
        config = ConfigManager()
        
        template = config.get_clash_template()
        
        assert isinstance(template, dict)
        # Clash 模板应该包含基本字段
        if template:
            assert 'port' in template or 'proxies' in template

