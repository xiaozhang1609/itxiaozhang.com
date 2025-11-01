---
title: Bilibili粉丝数据获取工具
permalink: /bilibili-followers-data-fetcher-python-tutorial-guide/
date: 2025-11-01 18:06:16
description: 本文介绍了一个基于Python开发的Bilibili粉丝数据获取工具，支持批量获取粉丝信息并生成HTML展示页面。文章详细讲解了Cookie获取方法、环境配置、使用步骤和常见问题解决方案，并提供完整的源码。适合UP主进行粉丝统计分析和数据备份使用。
category:
tags:
- Python
- 爬虫
- 哔哩哔哩
---

> 原文地址：<https://itxiaozhang.com/bilibili-followers-data-fetcher-python-tutorial-guide/>  
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://itxiaozhang.netlify.app/)咨询。    

# Bilibili粉丝数据获取工具使用指南

## 一、工具介绍

本工具是一个基于Python开发的Bilibili粉丝数据获取程序，能够批量获取用户的粉丝信息并生成美观的HTML展示页面。

**主要功能：**
- 批量获取Bilibili粉丝数据（最多1000个粉丝）
- 自动过滤默认头像用户，提升数据质量
- 生成响应式HTML页面，支持多设备查看
- 异步处理，提高数据获取效率

**适用场景：**
- UP主了解粉丝构成
- 制作粉丝感谢页面
- 个人数据统计备份

## 二、Cookie获取方法

### Chrome浏览器获取步骤：
1. 登录Bilibili账号
2. 按F12打开开发者工具
3. 切换到"Network"（网络）标签页
4. 刷新页面或随意点击一个链接
5. 在请求列表中找到任意一个请求
6. 在右侧"Headers"中找到"Cookie"字段
7. 复制完整的Cookie内容

### 安全注意事项：
- Cookie包含您的登录凭证，请妥善保管
- 不要将Cookie分享给他人
- 建议定期更新Cookie以保证安全性

## 三、环境准备

### 系统要求：
- Python 3.7 或更高版本
- 稳定的网络连接

### 依赖安装：
```bash
pip install aiohttp
```

## 四、使用步骤

### 1. 配置Cookie
打开 `bilibili_followers_fetcher.py` 文件，找到以下代码行：
```python
'Cookie': 'SESSDATA=你的SESSDATA内容'
```
将其中的SESSDATA内容替换为您从浏览器获取的真实Cookie中的SESSDATA部分。

### 2. 运行程序
在命令行中执行：
```bash
python bilibili_followers_fetcher.py
```

### 3. 查看结果
程序运行完成后，会在当前目录生成 `followers.html` 文件，用浏览器打开即可查看粉丝列表。

## 五、常见问题解决

### Cookie相关问题：
- **Cookie过期**：重新从浏览器获取最新Cookie
- **权限不足**：确认账号已正常登录Bilibili
- **格式错误**：检查Cookie是否完整复制

### 网络相关问题：
- **请求超时**：检查网络连接，稍后重试
- **API错误**：可能是请求频率过高，等待一段时间后重试
- **数据不完整**：网络不稳定导致，可重新运行程序

### 数据相关问题：
- **粉丝数量限制**：程序最多获取1000个粉丝（20页×50个）
- **部分粉丝缺失**：Bilibili API限制，属于正常现象
- **文件编码问题**：确保使用UTF-8编码打开HTML文件

## 六、注意事项

### 合规使用：
- 本工具仅供个人学习和研究使用
- 请遵守Bilibili平台的使用条款
- 不得将获取的数据用于商业用途

### 使用建议：
- 控制使用频率，避免对服务器造成压力
- 尊重用户隐私，不要泄露他人信息
- 建议在网络空闲时段使用

## 七、完整源码

以下是完整的Python源码：

```python
import asyncio
import aiohttp
import json
import html
import re
from pathlib import Path
from typing import List, Dict, Any

class BilibiliFetcher:
    def __init__(self):
        # 注意：请将下面的Cookie替换为您自己的真实Cookie
        self.headers = {
            'Cookie': 'SESSDATA=你的SESSDATA内容',
            'Origin': 'https://www.bilibili.com',
            'Referer': 'https://www.bilibili.com/',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        }
        self.session = None
        self.uid = None
        
    def encode_html(self, text: str) -> str:
        """HTML编码函数，与JavaScript版本保持一致"""
        if not isinstance(text, str):
            return ''
        
        # 基本HTML实体编码
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        
        # 处理空格：连续空格、行首行尾空格转换为&nbsp;
        text = re.sub(r' (?= )|(?<= ) |^ | $', '&nbsp;', text, flags=re.MULTILINE)
        
        # 换行符转换为<br />
        text = re.sub(r'\r\n|\r|\n', '<br />', text)
        
        return text
    
    async def create_session(self):
        """创建aiohttp会话"""
        self.session = aiohttp.ClientSession(headers=self.headers)
    
    async def close_session(self):
        """关闭aiohttp会话"""
        if self.session:
            await self.session.close()
    
    async def get_user_info(self) -> int:
        """获取自己的UID"""
        try:
            async with self.session.get('https://api.bilibili.com/x/web-interface/nav') as response:
                ujson = await response.json()
                
            if ujson['code'] != 0:
                print(f'获取用户信息失败: {ujson["message"]}')
                raise Exception(f'获取用户信息失败: {ujson["message"]}')
                
            self.uid = ujson['data']['mid']
            return self.uid
            
        except Exception as e:
            print(f'获取用户信息时出错: {str(e)}')
            raise
    
    async def get_followers_page(self, page: int) -> List[Dict[str, Any]]:
        """获取指定页的粉丝信息"""
        try:
            url = f'https://api.bilibili.com/x/relation/fans?vmid={self.uid}&ps=50&pn={page}'
            async with self.session.get(url) as response:
                data = await response.json()
                
            if data['code'] == 0 and data.get('data') and data['data'].get('list'):
                return data['data']['list']
            else:
                print(f'获取第{page}页粉丝信息失败: {data.get("message", "未知错误")}')
                return []
                
        except Exception as e:
            print(f'请求第{page}页时出错: {str(e)}')
            return []
    
    async def get_all_followers(self, max_pages: int = 20) -> List[Dict[str, Any]]:
        """获取所有粉丝信息"""
        followers = []
        
        # 获取前20页粉丝的信息，每页50个
        for i in range(1, max_pages + 1):
            page_followers = await self.get_followers_page(i)
            if not page_followers:
                break
            followers.extend(page_followers)
            
        return followers
    
    async def get_followers_detail_info(self, followers: List[Dict[str, Any]]) -> None:
        """获取所有粉丝的详细信息"""
        if not followers:
            return
            
        uids = [str(f['mid']) for f in followers]
        uid_str = ','.join(uids)
        
        try:
            url = f'https://api.vc.bilibili.com/x/im/user_infos?uids={uid_str}'
            async with self.session.get(url) as response:
                cjson = await response.json()
                
            if cjson['code'] == 0 and cjson.get('data'):
                # 将详细信息合并到粉丝对象中
                for info in cjson['data']:
                    follower = next((f for f in followers if f['mid'] == info['mid']), None)
                    if follower:
                        follower.update(info)
                        
        except Exception as e:
            print(f'获取粉丝详细信息时出错: {str(e)}')
    
    async def get_followers_stats(self, followers: List[Dict[str, Any]]) -> None:
        """获取所有粉丝的粉丝数统计"""
        if not followers:
            return
            
        # 分批处理，每批最多20个
        followers_without_stat = [f['mid'] for f in followers]
        
        while followers_without_stat:
            batch = followers_without_stat[:20]
            followers_without_stat = followers_without_stat[20:]
            
            try:
                mids_str = ','.join(map(str, batch))
                url = f'https://api.bilibili.com/x/relation/stats?mids={mids_str}'
                async with self.session.get(url) as response:
                    sjson = await response.json()
                    
                if sjson['code'] == 0 and sjson.get('data'):
                    # 将统计信息合并到粉丝对象中
                    for mid_str, stat in sjson['data'].items():
                        mid = int(mid_str)
                        follower = next((f for f in followers if f['mid'] == mid), None)
                        if follower:
                            follower.update(stat)
                            
            except Exception as e:
                print(f'获取粉丝统计信息时出错: {str(e)}')
    
    def filter_default_avatars(self, followers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """过滤掉使用默认头像的用户"""
        filtered = [f for f in followers if '/member/noface.jpg' not in f.get('face', '')]
        
        print(f'原始粉丝数量: {len(followers)}')
        print(f'过滤后粉丝数量: {len(filtered)}')
        print(f'已过滤掉 {len(followers) - len(filtered)} 个默认头像用户')
        
        return filtered
    
    def generate_html(self, followers: List[Dict[str, Any]], output_file: str = 'followers.html') -> None:
        """生成HTML文件"""
        content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>粉丝列表</title>
  <style>
    * {{
      font-family: Lato, 'PingFang SC', 'Microsoft YaHei', sans-serif;
      font-size: 20px;
      overflow-wrap: anywhere;
      text-align: justify;
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }}

    body {{
      background: #f5f7fa;
      padding: 20px;
      line-height: 1.6;
      min-height: 100vh;
    }}

    .container {{
      width: 100%;
      max-width: none;
    }}

    .header {{
      text-align: center;
      margin-bottom: 30px;
    }}

    .header h1 {{
      font-size: 32px;
      font-weight: 600;
      color: #1f2937;
      margin-bottom: 8px;
    }}

    .header p {{
      font-size: 16px;
      color: #6b7280;
    }}

    .followers-content {{
      background: white;
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
      width: 100%;
    }}

    div.inline-block {{
      display: inline-block;
      margin-right: 5px;
      margin-bottom: 10px;
    }}

    div.info {{
      align-items: center;
      display: flex;
    }}

    div.image-wrap {{
      margin-right: 5px;
      position: relative;
    }}

    img {{
      vertical-align: middle;
    }}

    img.face {{
      border-radius: 50%;
      height: 60px;
    }}

    img.icon-face-nft {{
      border: 2px solid var(--background-color);
      box-sizing: border-box;
    }}

    div.image-wrap.has-frame img.face {{
      height: 51px;
      padding: 19.5px;
    }}

    div.image-wrap.has-frame img.face-frame {{
      height: 90px;
      left: calc(50% - 45px);
      position: absolute;
      top: 0;
    }}

    div.image-wrap img.face-icon {{
      border-radius: 50%;
      height: 18px;
      left: calc(50% + 13.25px);
      position: absolute;
      top: calc(50% + 13.25px);
    }}

    div.image-wrap img.face-icon.second {{
      left: calc(50% - 3.75px);
    }}

    div.image-wrap.has-frame img.face-icon {{
      left: calc(50% + 9px);
      top: calc(50% + 9px);
    }}

    div.image-wrap.has-frame img.face-icon.second {{
      left: calc(50% - 8px);
    }}

    @media (max-width: 768px) {{
      body {{
        padding: 10px;
      }}

      .header h1 {{
        font-size: 24px;
      }}

      .followers-content {{
        padding: 15px;
      }}

      * {{
        font-size: 18px;
      }}

      img.face {{
        height: 50px;
      }}
    }}

    @media (max-width: 480px) {{
      body {{
        padding: 5px;
      }}

      .followers-content {{
        padding: 10px;
      }}

      * {{
        font-size: 16px;
      }}

      img.face {{
        height: 40px;
      }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>粉丝列表</h1>
      <p>共 {len(followers)} 位粉丝（已过滤默认头像用户）</p>
    </div>

    <div class="followers-content">
      {''.join([f'<div class="inline-block"><div class="info"><div class="image-wrap"><img class="face" src="{f.get("face", "")}" referrerpolicy="no-referrer" /></div> <div><strong>{self.encode_html(f.get("name") or f.get("uname", ""))}</strong></div></div></div>' for f in followers])}
    </div>
  </div>
</body>
</html>'''

        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f'成功生成粉丝列表HTML文件，共包含 {len(followers)} 个粉丝')

async def main():
    """主函数"""
    fetcher = BilibiliFetcher()
    
    try:
        # 创建会话
        await fetcher.create_session()
        
        # 获取用户UID
        await fetcher.get_user_info()
        
        # 获取所有粉丝信息
        followers = await fetcher.get_all_followers(max_pages=20)
        
        # 获取所有粉丝的详细信息
        await fetcher.get_followers_detail_info(followers)
        
        # 获取所有粉丝的粉丝数
        await fetcher.get_followers_stats(followers)
        
        # 过滤掉使用默认头像的用户
        filtered_followers = fetcher.filter_default_avatars(followers)
        
        # 生成HTML文件
        fetcher.generate_html(filtered_followers, 'followers.html')
        
    except Exception as e:
        print(f'程序运行出错: {str(e)}')
        return 1
        
    finally:
        # 关闭会话
        await fetcher.close_session()
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        exit(1)
    except Exception as error:
        print(f'程序运行出错: {str(error)}')
        exit(1)
```

## 八、总结

本工具为Bilibili用户提供了一个简单易用的粉丝数据获取解决方案。通过异步处理和批量API调用，能够高效地获取和展示粉丝信息。使用时请注意遵守相关规定，合理使用，保护用户隐私。

如有问题或建议，欢迎反馈交流。

## 视频版本

- [哔哩哔哩](https://space.bilibili.com/3546607630944387)
- [YouTube](https://www.youtube.com/@itxiaozhang)

---
▶ 如果您需要远程电脑维修或者编程开发，请[加我微信](https://itxiaozhang.netlify.app/)咨询。 
▶ 本网站的部分内容可能来源于网络，仅供大家学习与参考，如有侵权请联系我核实删除。  
▶ **我是小章，目前全职提供电脑维修和IT咨询服务。如果您有任何电脑相关的问题，都可以问我噢。**  
