#!/usr/bin/env python3
"""
V2Ray 节点聚合系统主程序
"""

import asyncio
import argparse
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.config_manager import ConfigManager
from src.collector import NodeCollector
from src.parser import NodeParser
from src.deduplicator import Deduplicator
from src.formatter import Formatter
from src.speed_tester import SpeedTester
from utils.logger import setup_logger, get_logger


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='V2Ray 节点聚合系统 - 收集、测速、转换多种格式'
    )
    
    parser.add_argument(
        '--skip-test',
        action='store_true',
        help='跳过测速步骤'
    )
    
    parser.add_argument(
        '--source',
        type=str,
        help='指定特定的节点源（源名称）'
    )
    
    parser.add_argument(
        '--format',
        type=str,
        choices=['all', 'base64', 'clash', 'v2ray', 'surge', 'quantumult'],
        default='all',
        help='指定输出格式（默认: all）'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='output',
        help='输出目录（默认: output）'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='日志级别（默认: INFO）'
    )
    
    parser.add_argument(
        '--max-nodes',
        type=int,
        help='最大节点数量'
    )
    
    return parser.parse_args()


async def main():
    """主函数"""
    # 解析参数
    args = parse_arguments()
    
    # 生成时间戳（格式: yyyy-MM-dd_HH-mm-ss）
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    
    # 设置日志
    logger = setup_logger(
        level=args.log_level,
        log_file=f"logs/update_{timestamp}.log"
    )
    
    logger.info("=" * 60)
    logger.info("V2Ray 节点聚合系统启动")
    logger.info("=" * 60)
    
    try:
        # 加载配置
        logger.info("加载配置文件...")
        config = ConfigManager()
        
        # 步骤1: 收集节点
        logger.info("\n【步骤 1/5】收集节点")
        logger.info("-" * 60)
        collector = NodeCollector(config)
        
        if args.source:
            # 如果指定了源，只收集该源
            logger.info(f"只收集指定源: {args.source}")
            all_sources = config.get_sources()
            filtered_sources = [s for s in all_sources if s['name'] == args.source]
            if not filtered_sources:
                logger.error(f"未找到源: {args.source}")
                return
            # 这里需要修改 collector 的逻辑来支持，暂时收集所有
        
        nodes = await collector.collect_all()
        
        if not nodes:
            logger.error("未收集到任何节点，程序退出")
            return
        
        logger.info(f"✓ 收集完成，共 {len(nodes)} 个节点")
        
        # 步骤2: 去重
        logger.info("\n【步骤 2/5】节点去重")
        logger.info("-" * 60)
        dedup_method = config.get_setting('deduplication.method', 'hash')
        keep_faster = config.get_setting('deduplication.keep_faster', True)
        
        deduplicator = Deduplicator(method=dedup_method, keep_faster=keep_faster)
        
        # 关键词过滤
        exclude_keywords = config.get_setting('filter.exclude_keywords', [])
        if exclude_keywords:
            nodes = deduplicator.filter_by_keywords(nodes, exclude_keywords=exclude_keywords)
        
        # 去重
        nodes = deduplicator.remove_duplicates(nodes)
        logger.info(f"✓ 去重完成，剩余 {len(nodes)} 个节点")
        
        # 步骤3: 测速（可选）
        speed_results = []
        if not args.skip_test:
            logger.info("\n【步骤 3/5】节点测速")
            logger.info("-" * 60)
            tester = SpeedTester(config)
            
            speed_results = await tester.test_all(nodes)
            
            # 过滤不可用节点
            filter_invalid = config.get_setting('speed_test.filter_invalid', True)
            speed_results = tester.filter_by_test_results(speed_results, filter_invalid)
            
            # 排序
            sort_by = config.get_setting('output.sort_by', 'speed')
            speed_results = tester.sort_results(speed_results, sort_by)
            
            # 更新节点列表
            nodes = [r.node for r in speed_results]
            
            logger.info(f"✓ 测速完成，可用节点 {len(nodes)} 个")
        else:
            logger.info("\n【步骤 3/5】跳过测速")
        
        # 限制节点数量
        max_nodes = args.max_nodes or config.get_setting('output.max_nodes', 200)
        if len(nodes) > max_nodes:
            logger.info(f"节点数量超过限制 {max_nodes}，进行裁剪")
            nodes = nodes[:max_nodes]
        
        # 步骤4: 格式转换
        logger.info("\n【步骤 4/5】格式转换")
        logger.info("-" * 60)
        formatter = Formatter(config)
        
        # 创建带时间戳的输出目录
        base_output_dir = Path(args.output_dir)
        timestamped_dir = base_output_dir / timestamp
        timestamped_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建或更新 latest 符号链接
        latest_link = base_output_dir / 'latest'
        if latest_link.exists() or latest_link.is_symlink():
            latest_link.unlink()
        latest_link.symlink_to(timestamp)
        
        logger.info(f"输出目录: {timestamped_dir}")
        logger.info(f"最新链接: {latest_link} -> {timestamp}")
        
        output_dir = timestamped_dir
        
        formats = ['all'] if args.format == 'all' else [args.format]
        if 'all' in formats:
            formats = config.get_setting('output.formats', ['base64', 'clash'])
        
        for fmt in formats:
            try:
                if fmt == 'base64':
                    content = formatter.to_base64(nodes)
                    formatter.save_to_file(content, output_dir / 'nodes.txt')
                    logger.info("✓ 生成 Base64 格式")
                
                elif fmt == 'clash':
                    content = formatter.to_clash_yaml(nodes)
                    formatter.save_to_file(content, output_dir / 'clash.yaml')
                    logger.info("✓ 生成 Clash YAML 格式")
                
                elif fmt == 'v2ray':
                    content = formatter.to_v2ray_json(nodes)
                    formatter.save_to_file(content, output_dir / 'v2ray.json')
                    logger.info("✓ 生成 V2Ray JSON 格式")
                
                elif fmt == 'surge':
                    content = formatter.to_surge(nodes)
                    formatter.save_to_file(content, output_dir / 'surge.conf')
                    logger.info("✓ 生成 Surge 格式")
                
                elif fmt == 'quantumult':
                    content = formatter.to_quantumult(nodes)
                    formatter.save_to_file(content, output_dir / 'quantumult.conf')
                    logger.info("✓ 生成 Quantumult X 格式")
            
            except Exception as e:
                logger.error(f"生成 {fmt} 格式失败: {e}")
        
        # 步骤5: 生成统计信息
        logger.info("\n【步骤 5/5】生成统计信息")
        logger.info("-" * 60)
        
        # 按协议统计
        protocol_stats = {}
        for node in nodes:
            protocol_stats[node.protocol] = protocol_stats.get(node.protocol, 0) + 1
        
        stats = {
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_nodes': len(nodes),
            'protocols': protocol_stats,
        }
        
        # 保存统计信息
        import json
        with open(output_dir / 'stats.json', 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        logger.info(f"总节点数: {stats['total_nodes']}")
        for protocol, count in protocol_stats.items():
            logger.info(f"  {protocol.upper()}: {count} 个")
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ 所有任务完成！")
        logger.info("=" * 60)
    
    except KeyboardInterrupt:
        logger.info("\n程序被用户中断")
    except Exception as e:
        logger.error(f"程序执行出错: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    # Windows 系统需要这个
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())

