---
title: HMDB代谢物信息批量获取工具：支持PPM误差计算的Python代谢组学数据提取解决方案
url: /hmdb-metabolite-batch-extractor-python-tool-with-ppm-error-calculation/
date: '2025-09-15 09:31:16 +0800'
description: 文介绍了一个专业的HMDB代谢物信息批量获取工具，该工具支持双离子模式、灵活的Da/PPM误差计算、智能缓存机制和并发处理。通过Python实现，具备企业级稳定性和用户友好的配置界面，为代谢组学研究提供高效的数据获取和代谢物注释解决方案，显著提升科研效率。
categories:
  - 编程开发
tags:
  - hmdb
  - python
  - 代谢组学工具
  - 质谱数据分析
author: IT小章
---
> 本文对应60号代码。

## 这个程序是做什么的？

HMDB代谢物信息批量获取工具是一个专业的生物信息学工具，专门用于从HMDB（Human Metabolome Database，人类代谢组数据库）批量获取代谢物的详细信息。该工具通过输入代谢物的质量数，自动搜索并提取相关的代谢物数据，为代谢组学研究提供高效的数据获取解决方案。

### 核心用途

- **代谢组学研究**：为质谱分析结果提供代谢物注释
- **化合物鉴定**：根据精确质量数快速匹配可能的代谢物
- **数据库查询**：批量获取代谢物的生物学信息
- **科研辅助**：为生物医学研究提供代谢物数据支持

## 主要功能

### 1. 双离子模式支持

- **正离子模式**：支持M+H、M+Li、M+NH4、M+Na等加合离子
- **负离子模式**：支持M-H加合离子
- **智能模式选择**：用户可根据实验条件选择合适的离子化模式

### 2. 灵活的误差计算方式

- **固定Da误差**：传统的绝对误差计算方式
- **PPM相对误差**：科学的相对误差计算，公式为 `(实验值-理论值)/理论值×10^6`
- **用户可配置**：通过da.txt和ppm.txt文件自定义误差参数

### 3. 智能缓存机制

- **本地缓存**：避免重复请求相同的代谢物数据
- **断点续传**：支持程序中断后继续处理
- **批量保存**：优化I/O操作，提高处理效率

### 4. 高效并发处理

- **多线程处理**：同时处理多个HMDB ID查询
- **智能限流**：控制并发数量，避免服务器过载
- **进度显示**：实时显示处理进度和统计信息

### 5. robust错误处理

- **智能重试**：针对网络错误和服务器503错误的特殊处理
- **指数退避**：逐步增加重试间隔，提高成功率
- **详细日志**：完整记录处理过程和错误信息

### 6. 丰富的数据提取

程序能够提取以下代谢物信息：

- 基本信息：HMDB ID、通用名称、化学式
- 分类信息：超类、类别、子类
- 生物学性质：内源性、组织分布
- 数据库交叉引用：KEGG、ChEBI、METLIN ID
- 结构信息：分子结构图链接

## 程序特点

### 1. 用户友好的交互界面

```
📁 检查输入文件:
   ✓ positive.txt (5 个质量数)
   ✓ negative.txt (2 个质量数)
   ✓ da.txt (3 个Da选项)
   ✓ ppm.txt (4 个PPM选项)

⚙️ 请选择误差计算方式:
   1. 固定Da误差模式 (使用da.txt配置)
   2. PPM相对误差模式 (使用ppm.txt配置)
```

### 2. 高度可配置性

- **配置文件驱动**：所有参数都可通过配置文件调整
- **多精度选择**：支持不同精度要求的应用场景
- **向后兼容**：保持与旧版本的兼容性

### 3. 企业级稳定性

- **连接池管理**：优化网络连接使用
- **内存优化**：智能缓存管理，避免内存溢出
- **异常恢复**：程序崩溃后可从断点继续

### 4. 性能优化

- **批量处理**：一次性处理大量质量数
- **并发控制**：平衡处理速度和服务器负载
- **缓存命中率统计**：实时监控缓存效果

## 部分代码

```python
import requests
import json
import time
from typing import List, Dict, Any
from abc import ABC, abstractmethod

class BaseExtractor(ABC):
    """抽象基类 - 数据提取器接口"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """创建HTTP会话"""
        session = requests.Session()
        session.headers.update(self.config.get('headers', {}))
        return session
    
    @abstractmethod
    def search(self, query: str) -> List[str]:
        """搜索方法 - 子类必须实现"""
        pass
    
    @abstractmethod
    def extract(self, item_id: str) -> Dict[str, Any]:
        """提取方法 - 子类必须实现"""
        pass

class CacheManager:
    """缓存管理器"""
    
    def __init__(self, cache_file: str):
        self.cache_file = cache_file
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def get(self, key: str) -> Any:
        return self.data.get(key)
    
    def set(self, key: str, value: Any):
        self.data[key] = value
        self._save()
    
    def _save(self):
        with open(self.cache_file, 'w') as f:
            json.dump(self.data, f)

class DataProcessor:
    """数据处理器"""
    
    @staticmethod
    def process_batch(items: List[str], processor_func) -> List[Dict]:
        """批量处理数据"""
        results = []
        for item in items:
            try:
                result = processor_func(item)
                if result:
                    results.append(result)
            except Exception as e:
                print(f"处理失败: {item}, 错误: {e}")
        return results
    
    @staticmethod
    def save_results(data: List[Dict], filename: str):
        """保存结果"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

class WebExtractor(BaseExtractor):
    """具体实现类"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.cache = CacheManager(config.get('cache_file', 'cache.json'))
    
    def search(self, query: str) -> List[str]:
        """搜索实现"""
        # 检查缓存
        cache_key = f"search_{query}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        # 模拟网络请求
        time.sleep(1)  # 请求延迟
        
        # 这里是具体的搜索逻辑
        # 实际项目中会有具体的API调用和数据解析
        results = self._perform_search(query)
        
        # 缓存结果
        self.cache.set(cache_key, results)
        return results
    
    def extract(self, item_id: str) -> Dict[str, Any]:
        """提取实现"""
        # 检查缓存
        cached = self.cache.get(item_id)
        if cached:
            return cached
        
        # 模拟网络请求
        time.sleep(0.5)
        
        # 这里是具体的提取逻辑
        data = self._perform_extraction(item_id)
        
        # 缓存结果
        if data:
            self.cache.set(item_id, data)
        
        return data
    
    def _perform_search(self, query: str) -> List[str]:
        """执行搜索 - 具体实现会根据目标网站调整"""
        # 这里会有具体的HTTP请求和HTML解析逻辑
        return [f"item_{i}" for i in range(3)]  # 示例返回
    
    def _perform_extraction(self, item_id: str) -> Dict[str, Any]:
        """执行提取 - 具体实现会根据目标网站调整"""
        # 这里会有具体的数据提取逻辑
        return {
            'id': item_id,
            'title': f'Title for {item_id}',
            'data': f'Data for {item_id}'
        }

class Application:
    """应用程序主类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.extractor = WebExtractor(config)
        self.processor = DataProcessor()
    
    def run(self, queries: List[str]):
        """运行应用程序"""
        all_results = []
        
        for query in queries:
            # 搜索相关项目
            items = self.extractor.search(query)
            
            # 提取详细数据
            for item_id in items:
                data = self.extractor.extract(item_id)
                if data:
                    data['query'] = query
                    all_results.append(data)
        
        # 保存结果
        self.processor.save_results(all_results, 'results.json')
        print(f"完成处理，共获取 {len(all_results)} 条数据")

def main():
    """主函数"""
    # 配置参数
    config = {
        'headers': {'User-Agent': 'Generic-Bot/1.0'},
        'cache_file': 'app_cache.json',
        'delay': 1.0
    }
    
    # 创建应用实例
    app = Application(config)
    
    # 示例查询列表
    test_queries = ['query1', 'query2', 'query3']
    
    # 运行程序
    app.run(test_queries)

if __name__ == '__main__':
    main()
```

## 技术亮点

1. **科学的误差计算**：支持PPM相对误差，适应不同质量范围的化合物
2. **智能网络处理**：针对HMDB服务器特点优化的请求策略
3. **高效缓存机制**：多层缓存设计，显著提高处理效率
4. **robust错误处理**：全面的异常处理和恢复机制
5. **用户友好设计**：直观的配置文件和交互界面

## 视频版本

- [哔哩哔哩](https://space.bilibili.com/3546607630944387)
- [YouTube](https://www.youtube.com/@itxiaozhang)


> 原文地址：<https://itxiaozhang.com/hmdb-metabolite-batch-extractor-python-tool-with-ppm-error-calculation/>
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://zhang9.cn)咨询。 
