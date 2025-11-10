#!/usr/bin/env python3
"""
重建 history.json
扫描 gh-pages 分支的 history 目录，为所有历史版本生成 history.json
"""
import json
import os
import sys
from pathlib import Path

def rebuild_history():
    print("开始重建 history.json...")
    
    # 定义历史版本目录（从 gh-pages 分支看到的）
    versions_data = [
        {"timestamp": "2025-11-10_02-45-19"},
        {"timestamp": "2025-11-09_20-59-03"},
        {"timestamp": "2025-11-09_14-48-03"},
        {"timestamp": "2025-11-09_10-14-28"},
        {"timestamp": "2025-11-09_02-46-01"},
        {"timestamp": "2025-11-08_20-58-37"},
        {"timestamp": "2025-11-08_14-47-27"},
        {"timestamp": "2025-11-08_10-04-13"},
        {"timestamp": "2025-11-08_02-47-55"},
        {"timestamp": "2025-11-07_21-05-18"},
    ]
    
    history = {"versions": []}
    
    for version_data in versions_data:
        timestamp = version_data["timestamp"]
        
        # 尝试从 GitHub Pages 下载该版本的 stats.json
        import urllib.request
        stats_url = f"https://miaolitao.github.io/V2Ray/history/{timestamp}/stats.json"
        
        try:
            print(f"下载 {timestamp}/stats.json...")
            with urllib.request.urlopen(stats_url) as response:
                stats = json.loads(response.read().decode())
                
            version = {
                "timestamp": timestamp,
                "update_time": stats.get('update_time', ''),
                "total_nodes": stats.get('total_nodes', 0),
                "valid_nodes": stats.get('valid_nodes', 0),
                "protocols": stats.get('protocols', {})
            }
            
            history["versions"].append(version)
            print(f"  ✓ {timestamp}: {stats.get('total_nodes', 0)} 节点")
            
        except Exception as e:
            print(f"  ✗ 下载失败: {e}")
            # 如果下载失败，添加占位记录
            version = {
                "timestamp": timestamp,
                "update_time": "",
                "total_nodes": 0,
                "valid_nodes": 0,
                "protocols": {}
            }
            history["versions"].append(version)
    
    # 保存到文件
    output_file = "history.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 历史记录已重建！")
    print(f"   文件: {output_file}")
    print(f"   版本数: {len(history['versions'])}")
    
    return history

if __name__ == "__main__":
    history = rebuild_history()
    
    # 打印 JSON 供复制
    print("\n" + "="*70)
    print("完整的 history.json 内容：")
    print("="*70)
    print(json.dumps(history, ensure_ascii=False, indent=2))
