---
title: 'Python爬虫实战: 58同城房产信息自动化采集'
permalink: /python-web-crawler-58city-real-estate-data-collection/
date: 2024-12-01 19:28:00
description: 这是一个基于Python开发的58同城房产信息采集系统,主要用于自动采集商铺、写字楼、厂房和生意转让等房产信息。系统提供图形界面操作,支持多城市数据采集。
category:
- 编程案例
tags:
- python
- 爬虫
- 58同城
---

> 原文地址：<https://itxiaozhang.com/python-web-crawler-58city-real-estate-data-collection/>  

## 1. 简介

这是一个基于Python开发的58同城房产信息采集系统,主要用于自动采集商铺、写字楼、厂房和生意转让等房产信息。系统提供图形界面操作,支持多城市数据采集。

## 2. 主要功能

- 多城市房产信息采集
- 多线程并发处理
- 自动代理IP切换
- 数据实时入库
- 自动去重过滤
- 定时采集更新

## 3. 技术特点

### 多线程采集

使用Python threading实现并发采集,提高效率。

### 代理IP池

自动维护代理IP池,避免被反爬:

```python
def roxies_ip(url):
    ip = requests.get(url).text
    proxies_ip_lists = []
    for i in ip:
        proxies_ip_lists.append({'https': "//" + i})
    return proxies_ip_lists[0]
```

### 数据存储

采用MySQL存储数据,支持实时入库和查重。

## 4. 使用方法

1. 配置数据库信息
2. 设置代理IP接口
3. 选择目标城市和类型
4. 设置采集间隔
5. 启动采集任务

## 相关源码

```python
import sys
from time import sleep

from tkinter import messagebox
import tkinter
from tkinter import ttk

import random
import json
import re
import time
import datetime
import urllib3
import hashlib
import threading
from bs4 import BeautifulSoup
import pymysql as MySQLdb
from dbutils.pooled_db import PooledDB
import requests

# 数据库配置
localhost = "xxx.xxx.xxx.xxx"  # 应屏蔽IP地址
username = "xxxxx"  # 应屏蔽用户名
pwd = "xxxxxxxx"  # 应屏蔽密码
db = "xxxxx"  # 应屏蔽数据库名
city_f = {"北京": {"北京": "bj|1"}, "上海": {"上海": "sh|2"}, "天津": {"天津": "tj|18"}, "重庆": {"重庆": "cq|37"},
          "安徽": {"合肥": "hf|837", "芜湖": "wuhu|2045", "蚌埠": "bengbu|3470", "阜阳": "fy|2325", "淮南": "hn|2319",
                 "安庆": "anqing|3251", "宿州": "suzhou|3359", "六安": "la|2328", "淮北": "huaibei|9357", "滁州": "chuzhou|10266",
                 "马鞍山": "mas|2039", "铜陵": "tongling|10285", "宣城": "xuancheng|5633", "亳州": "bozhou|2329",
                 "黄山": "huangshan|2323", "池州": "chizhou|10260", "巢湖": "ch|10229", "和县": "hexian|10892",
                 "霍邱": "hq|11226", "桐城": "tongcheng|11296", "宁国": "ningguo|5645", "天长": "tianchang|10273",
                 "东至": "dongzhi|10262", "无为": "wuweixian|10232"},
          "福建": {"福州": "fz|304", "厦门": "xm|606", "泉州": "qz|291", "莆田": "pt|2429", "漳州": "zhangzhou|710",
                 "宁德": "nd|7951", "三明": "sm|2048", "南平": "np|10291", "龙岩": "ly|6752", "武夷山": "wuyishan|10761",
                 "石狮": "shishi|296", "晋江": "jinjiangshi|297", "南安": "nananshi|293", "龙海": "longhai|713",
                 "上杭": "shanghangxian|6757", "福安": "fuanshi|7969", "福鼎": "fudingshi|7970", "安溪": "anxixian|7100",
                 "永春": "yongchunxian|7101", "永安": "yongan|2133", "漳浦": "zhangpu|717"},
          "广东": {"深圳": "sz|4", "广州": "gz|3", "东莞": "dg|413", "佛山": "fs|222", "中山": "zs|771", "珠海": "zh|910",
                 "惠州": "huizhou|722", "江门": "jm|629", "汕头": "st|783", "湛江": "zhanjiang|791", "肇庆": "zq|901",
                 "茂名": "mm|679", "揭阳": "jy|927", "梅州": "mz|9389", "清远": "qingyuan|7303", "阳江": "yj|2284",
                 "韶关": "sg|2192", "河源": "heyuan|10467", "云浮": "yf|10485", "汕尾": "sw|9449", "潮州": "chaozhou|10461",
                 "台山": "taishan|11263", "阳春": "yangchun|8566", "顺德": "sd|8716", "惠东": "huidong|725", "博罗": "boluo|726",
                 "海丰": "haifengxian|9444", "开平": "kaipingshi|634", "陆丰": "lufengshi|9456"},
          "广西": {"南宁": "nn|845", "柳州": "liuzhou|7133", "桂林": "gl|1039", "玉林": "yulin|2337", "梧州": "wuzhou|2046",
                 "北海": "bh|10536", "贵港": "gg|6770", "钦州": "qinzhou|2335", "百色": "baise|10513", "河池": "hc|2340",
                 "来宾": "lb|10552", "贺州": "hezhou|10549", "防城港": "fcg|10539", "崇左": "chongzuo|10524",
                 "桂平": "guipingqu|6774", "北流": "beiliushi|9168", "博白": "bobaixian|9173", "岑溪": "cenxi|2119"},
          "贵州": {"贵阳": "gy|2015", "遵义": "zunyi|7620", "黔东南": "qdn|9363", "黔南": "qn|10492", "六盘水": "lps|10506",
                 "毕节": "bijie|10564", "铜仁": "tr|10417", "安顺": "anshun|7468", "黔西南": "qxn|10434",
                 "仁怀": "renhuaishi|7628", "清镇": "qingzhen|12703"},
          "甘肃": {"兰州": "lz|952", "天水": "tianshui|8601", "白银": "by|10304", "庆阳": "qingyang|10475", "平凉": "pl|7154",
                 "酒泉": "jq|10387", "张掖": "zhangye|10454", "武威": "wuwei|10448", "定西": "dx|10322", "金昌": "jinchang|7428",
                 "陇南": "ln|10415", "临夏": "linxia|7112", "嘉峪关": "jyg|10362", "甘南": "gn|10343", "敦煌": "dunhuang|10390"},
          "海南": {"海口": "haikou|2053", "三亚": "sanya|2422", "五指山": "wzs|9952", "三沙": "sansha|13722", "琼海": "qh|10136",
                 "文昌": "wenchang|9984", "万宁": "wanning|10022", "屯昌": "tunchang|10044", "琼中": "qiongzhong|10064",
                 "陵水": "lingshui|10184", "东方": "df|10250", "定安": "da|10303", "澄迈": "cm|10331", "保亭": "baoting|10367",
                 "白沙": "baish|10380", "儋州": "danzhou|10394"},
          "河南": {"郑州": "zz|342", "洛阳": "luoyang|556", "新乡": "xx|1016", "南阳": "ny|592", "许昌": "xc|977",
                 "平顶山": "pds|1005", "安阳": "ay|1096", "焦作": "jiaozuo|3266", "商丘": "sq|1029", "开封": "kaifeng|2342",
                 "濮阳": "puyang|2346", "周口": "zk|933", "信阳": "xy|8694", "驻马店": "zmd|1067", "漯河": "luohe|2347",
                 "三门峡": "smx|9317", "鹤壁": "hb|2344", "济源": "jiyuan|9918", "明港": "mg|8541", "鄢陵": "yanling|9123",
                 "禹州": "yuzhou|979", "长葛": "changge|9344", "灵宝": "lingbaoshi|9307", "杞县": "qixianqu|7389",
                 "汝州": "ruzhou|1010", "项城": "xiangchengshi|935", "偃师": "yanshiqu|7121", "长垣": "changyuan|5936",
                 "滑县": "huaxian|5405", "林州": "linzhou|1101", "沁阳": "qinyang|3268", "孟州": "mengzhou|3267",
                 "温县": "wenxian|7312", "尉氏": "weishixian|7391", "兰考": "lankaoxian|7393", "通许": "tongxuxian|7390",
                 "新安": "lyxinan|11217", "伊川": "yichuan|11220", "孟津": "mengjinqu|7122", "宜阳": "lyyiyang|11219",
                 "舞钢": "wugang|1011", "永城": "yongcheng|1032", "睢县": "suixian|1038", "鹿邑": "luyi|939",
                 "渑池": "yingchixian|9322", "沈丘": "shenqiu|942", "太康": "taikang|938", "商水": "shangshui|936",
                 "淇县": "qixianq|9186", "浚县": "junxian|9185", "范县": "fanxian|7285", "固始": "gushixian|8698",
                 "淮滨": "huaibinxian|8702", "邓州": "dengzhou|595", "新野": "xinye|603"},
          "黑龙江": {"哈尔滨": "hrb|202", "大庆": "dq|375", "齐齐哈尔": "qqhr|5853", "牡丹江": "mdj|3489", "绥化": "suihua|6718",
                  "佳木斯": "jms|6776", "鸡西": "jixi|7289", "双鸭山": "sys|9837", "鹤岗": "hegang|9061", "黑河": "heihe|9862",
                  "伊春": "yich|9773", "七台河": "qth|9848", "大兴安岭": "dxal|9878", "安达": "shanda|6720",
                  "肇东": "shzhaodong|6721", "肇州": "zhaozhou|382"},
          "湖北": {"武汉": "wh|158", "宜昌": "yc|858", "襄阳": "xf|891", "荆州": "jingzhou|3479", "十堰": "shiyan|2032",
                 "黄石": "hshi|1734", "孝感": "xiaogan|3434", "黄冈": "hg|2299", "恩�����": "es|2302", "荆门": "jingmen|2296",
                 "咸宁": "xianning|9617", "鄂州": "ez|9709", "随州": "suizhou|9656", "潜江": "qianjiang|9669", "天门": "tm|9517",
                 "仙桃": "xiantao|9736", "神农架": "snj|9605", "宜都": "yidou|864", "汉川": "hanchuan|3439", "枣阳": "zaoyang|896",
                 "武穴": "wuxueshi|7362", "钟祥": "zhongxiangshi|9119", "京山": "jingshanxian|9117", "沙洋": "shayangxian|9118",
                 "松滋": "songzi|3484", "广水": "guangshuishi|9657", "赤壁": "chibishi|9623", "老河口": "laohekou|895",
                 "谷城": "gucheng|899", "宜城": "yichengshi|897", "南漳": "nanzhang|898", "云梦": "yunmeng|3438",
                 "安陆": "anlu|3442", "大悟": "dawu|3437", "孝昌": "xiaochang|3436", "当阳": "dangyang|865",
                 "枝江": "zhijiang|866", "嘉鱼": "jiayuxian|9624", "随县": "suixia|9660"},
          "湖南": {"长沙": "cs|414", "株洲": "zhuzhou|1086", "益阳": "yiyang|10198", "常德": "changde|872", "衡阳": "hy|914",
                 "湘潭": "xiangtan|2047", "岳阳": "yy|821", "郴州": "chenzhou|5695", "邵阳": "shaoyang|2303", "怀化": "hh|5756",
                 "永州": "yongzhou|2307", "娄底": "ld|9481", "湘西": "xiangxi|10219", "张家界": "zjj|6788", "醴陵": "liling|1091",
                 "澧县": "lixian|876", "桂阳": "czguiyang|5699", "资兴": "zixing|5698", "永兴": "yongxing|5701",
                 "常宁": "changningshi|921", "祁东": "qidongxian|5690", "衡东": "hengdong|5693",
                 "冷水江": "lengshuijiangshi|9470", "涟源": "lianyuanshi|9471", "双峰": "shuangfengxian|9473",
                 "邵阳县": "shaoyangxian|6955", "邵东": "shaodongxian|6954", "沅江": "yuanjiangs|10201", "南县": "nanxian|10202",
                 "祁阳": "qiyang|8532", "湘阴": "xiangyin|828", "华容": "huarong|830", "慈利": "cilixian|6791",
                 "攸县": "zzyouxian|1095"},
          "河北": {"石家庄": "sjz|241", "保定": "bd|424", "唐山": "ts|276", "廊坊": "lf|772", "邯郸": "hd|572", "秦皇岛": "qhd|1078",
                 "沧州": "cangzhou|652", "邢台": "xt|751", "衡水": "hs|993", "张家口": "zjk|3328", "承德": "chengde|6760",
                 "定州": "dingzhou|8398", "馆陶": "gt|8706", "张北": "zhangbei|11201", "赵县": "zx|9048", "正定": "zd|3198",
                 "迁安市": "qianan|284", "任丘": "renqiu|656", "三河": "sanhe|776", "武安": "wuan|577",
                 "雄安新区": "xionganxinqu|111234", "燕郊": "lfyanjiao|12804", "涿州": "zhuozhou|428", "河间": "hejian|658",
                 "黄骅": "huanghua|657", "沧县": "cangxian|659", "磁县": "cixian|591", "涉县": "shexian|14059",
                 "霸州": "bazhou|775", "香河": "xianghe|5395", "固安": "lfguan|12803", "遵化市": "zunhua|283",
                 "迁西": "qianxixian|7061", "玉田": "yutianxian|7060", "滦南": "luannanxian|7066", "沙河": "shaheshi|755"},
          "江苏": {"苏州": "su|5", "南京": "nj|172", "无锡": "wx|93", "常州": "cz|463", "徐州": "xz|471", "南通": "nt|394",
                 "扬州": "yz|637", "盐城": "yancheng|613", "淮安": "ha|968", "连云港": "lyg|2049", "泰州": "taizhou|693",
                 "宿迁": "suqian|2350", "镇江": "zj|645", "沭阳": "shuyang|5772", "大丰": "dafeng|11279", "如皋": "rugao|397",
                 "启东": "qidong|400", "溧阳": "liyang|469", "海门": "haimen|399", "东海": "donghai|2147",
                 "扬中": "yangzhong|649", "兴化": "xinghuashi|699", "新沂": "xinyishi|478", "泰兴": "taixing|696",
                 "如东": "rudong|402", "邳州": "pizhou|477", "沛县": "xzpeixian|11349", "靖江": "jingjiang|698",
                 "建湖": "jianhu|618", "海安": "haian|401", "东台": "dongtai|615", "丹阳": "danyang|648",
                 "宝应县": "baoyingx|14451", "灌南": "guannan|2150", "灌云": "guanyun|2148", "姜堰": "jiangyan|697",
                 "金坛": "jintan|468", "昆山": "szkunshan|16", "泗洪": "sihong|5958", "泗阳": "siyang|5959", "句容": "jurong|650",
                 "射阳": "sheyang|621", "阜宁": "funingxian|620", "响水": "xiangshui|619", "盱眙": "xuyi|976",
                 "金湖": "jinhu|975", "江阴": "jiangyins|34984"},
          "江西": {"南昌": "nc|669", "赣州": "ganzhou|2363", "九江": "jj|2247", "宜春": "yichun|5709", "吉安": "ja|2364",
                 "上饶": "sr|10120", "萍乡": "px|2248", "抚州": "fuzhou|10134", "景德镇": "jdz|2360", "新余": "xinyu|10115",
                 "鹰潭": "yingtan|3209", "永新": "yxx|11077", "乐平": "lepingshi|9048", "进贤": "jinxian|677",
                 "分宜": "fenyi|10118", "丰城": "fengchengshi|5711", "樟树": "zhangshu|5713", "高安": "gaoan|5712",
                 "余江": "yujiang|3210", "南城": "nanchengx|10137", "浮梁": "fuliangxian|9071"},
          "吉林": {"长春": "cc|319", "吉林": "jl|700", "四平": "sp|10171", "延边": "yanbian|3184", "松原": "songyuan|2315",
                 "白城": "bc|5918", "通化": "th|10159", "白山": "baishan|10179", "辽源": "liaoyuan|2501",
                 "公主岭": "gongzhuling|10171", "梅河口": "meihekou|10162", "扶余": "fuyuxian|9085", "长岭": "changlingxian|9084",
                 "桦甸": "huadian|706", "磐石": "panshi|708", "梨树县": "lishu|10176"},
          "辽宁": {"沈阳": "sy|188", "大连": "dl|147", "鞍山": "as|523", "锦州": "jinzhou|2354", "抚顺": "fushun|5722",
                 "营口": "yk|5898", "盘锦": "pj|2041", "朝阳": "cy|10106", "丹东": "dandong|3445", "辽阳": "liaoyang|2038",
                 "本溪": "benxi|5845", "葫芦岛": "hld|10088", "铁岭": "tl|6729", "阜新": "fx|10097", "庄河": "pld|3306",
                 "瓦房店": "wfd|3279", "灯塔": "dengta|2071", "凤城": "fengcheng|3450", "北票": "beipiao|10109",
                 "开原": "kaiyuan|6733"},
          "宁夏": {"银川": "yinchuan|2054", "吴忠": "wuzhong|9962", "石嘴山": "szs|9971", "中卫": "zw|9951", "固原": "guyuan|2421"},
          "内蒙古": {"呼和浩特": "hu|811", "包头": "bt|801", "赤峰": "chifeng|6700", "鄂尔多斯": "erds|2037", "通辽": "tongliao|10015",
                  "呼伦贝尔": "hlbe|10039", "巴彦淖尔市": "bycem|10070", "乌兰察布": "wlcb|9993", "锡林郭勒": "xl|2408",
                  "兴安盟": "xam|9976", "乌海": "wuhai|2404", "阿拉善盟": "alsm|10083", "海拉尔": "hlr|2043"},
          "青海": {"西宁": "xn|2052", "海西": "hx|9902", "海北": "haibei|9917", "果洛": "guoluo|9936", "海东": "haidong|9909",
                 "黄南": "huangnan|9896", "玉树": "ys|9888", "海南": "hainan|10574", "格尔木": "geermushi|9904"},
          "山东": {"青岛": "qd|122", "济南": "jn|265", "烟台": "yt|228", "潍坊": "wf|362", "临沂": "linyi|505", "淄博": "zb|385",
                 "济宁": "jining|450", "泰安": "ta|686", "聊城": "lc|882", "威海": "weihai|518", "枣庄": "zaozhuang|961",
                 "德州": "dz|728", "日照": "rizhao|3177", "东营": "dy|623", "菏泽": "heze|5632", "滨州": "bz|944",
                 "莱芜": "lw|2292", "章丘": "zhangqiu|8680", "垦利": "kl|11313", "诸城": "zc|9146", "寿光": "shouguang|369",
                 "龙口": "longkou|233", "曹县": "caoxian|5638", "单县": "shanxian|5636", "肥城": "feicheng|690",
                 "高密": "gaomi|371", "广饶": "guangrao|627", "桓台": "huantaixian|7335", "莒县": "juxian|3180",
                 "莱州": "laizhou|235", "蓬莱": "penglai|237", "青州": "qingzhou|367", "荣成": "rongcheng|522",
                 "乳山": "rushan|520", "滕州": "tengzhou|967", "新泰": "xintai|689", "招远": "zhaoyuan|3325",
                 "邹城": "zoucheng|455", "邹平": "zouping|946", "临清": "linqing|884", "茌平": "chiping|887", "郓城": "hzyc|5637",
                 "博兴": "boxing|949", "东明": "dongming|5641", "巨野": "juye|5640", "无棣": "wudi|951", "齐河": "qihe|734",
                 "微山": "weishan|459", "禹城": "yuchengshi|731", "临邑": "linyixianq|739", "乐陵": "leling|730",
                 "莱阳": "laiyang|234", "宁津": "ningjin|733", "高唐": "gaotang|885", "莘县": "shenxian|888",
                 "阳谷": "yanggu|886", "冠县": "guanxian|890", "平邑": "pingyi|514", "郯城": "tancheng|510",
                 "沂源": "yiyuanxian|7334", "汶上": "wenshang|460", "梁山": "liangshanx|462", "利津": "lijin|628",
                 "沂南": "yinanxian|7301", "栖霞": "qixia|238", "宁阳": "ningyang|691", "东平": "dongping|692",
                 "昌邑": "changyishi|372", "安丘": "anqiu|370", "昌乐": "changle|373", "临朐": "linqu|374",
                 "鄄城": "juancheng|5635"},
          "山西": {"太原": "ty|740", "临汾": "linfen|5669", "大同": "dt|6964", "运城": "yuncheng|5653", "晋中": "jz|8854",
                 "长治": "changzhi|6921", "晋城": "jincheng|3350", "阳泉": "yq|8760", "吕梁": "lvliang|3222",
                 "忻州": "xinzhou|3453", "朔州": "shuozhou|9871", "临猗": "linyixian|9193", "清徐": "qingxu|10908",
                 "柳林": "liulin|3225", "高平": "gaoping|3354", "泽州": "zezhou|3353", "襄垣": "xiangyuanxian|6928",
                 "孝义": "xiaoyi|3227"},
          "陕西": {"西安": "xa|483", "咸阳": "xianyang|7453", "宝鸡": "baoji|2044", "渭南": "wn|5733", "汉中": "hanzhong|3163",
                 "榆林": "yl|5942", "延安": "yanan|8973", "安康": "ankang|3157", "商洛": "sl|9854", "铜川": "tc|9832",
                 "神木": "shenmu|5944", "韩城": "hancheng|5735", "府谷": "fugu|5945", "靖边": "jingbian|5947",
                 "定边": "dingbian|5948"},
          "四川": {"成都": "cd|102", "绵阳": "mianyang|1057", "德阳": "deyang|2373", "南充": "nanchong|2378", "宜宾": "yb|2380",
                 "自贡": "zg|6745", "乐山": "ls|3237", "泸州": "luzhou|2372", "达州": "dazhou|9799", "内江": "scnj|5928",
                 "遂宁": "suining|9688", "攀枝花": "panzhihua|2371", "眉山": "ms|9704", "广安": "ga|2381", "资阳": "zy|6803",
                 "凉山": "liangshan|9717", "广元": "guangyuan|9749", "雅安": "ya|9687", "巴中": "bazhong|9811", "阿坝": "ab|9817",
                 "甘孜": "ganzi|9764", "安岳": "anyuexian|6806", "广汉": "guanghanshi|8719", "简阳": "jianyangshi|6805",
                 "仁寿": "renshouxian|9706", "射洪": "shehongxian|9694", "大竹": "dazu|9806", "宣汉": "xuanhan|9804",
                 "渠县": "qux|9807", "长宁": "changningx|7148"},
          "新疆": {"乌鲁木齐": "xj|984", "昌吉": "changji|8582", "巴音郭楞": "bygl|9530", "伊犁": "yili|9472", "阿克苏": "aks|9499",
                 "喀什": "ks|9326", "哈密": "hami|7452", "克拉玛依": "klmy|2042", "博尔塔拉": "betl|9529", "吐鲁番": "tlf|9475",
                 "和田": "ht|9489", "石河子": "shz|9551", "克孜勒苏": "kzls|9519", "阿拉尔": "ale|9539", "五家渠": "wjq|9562",
                 "图木舒克": "tmsk|9559", "库尔勒": "kel|7168", "阿勒泰": "alt|18837", "塔城": "tac|18845"},
          "西藏": {"拉萨": "lasa|2055", "日喀则": "rkz|9615", "山南": "sn|9576", "林芝": "linzhi|9646", "昌都": "changdu|9648",
                 "那曲": "nq|9618", "阿里": "al|9678", "日土": "rituxian|9682", "改则": "gaizexian|9684"},
          "云南": {"昆明": "km|541", "曲靖": "qj|2389", "大理": "dali|2398", "红河": "honghe|2394", "玉溪": "yx|2040",
                 "丽江": "lj|2392", "文山": "ws|2395", "楚雄": "cx|2393", "西双版纳": "bn|2397", "昭通": "zt|9409", "德宏": "dh|9437",
                 "普洱": "pe|9444", "保山": "bs|2390", "临沧": "lincang|9422", "迪庆": "diqing|9432", "怒江": "nujiang|9462",
                 "弥勒": "milexian|8892", "安宁": "anningshi|547", "宣威": "xuanwushi|7533"},
          "浙江": {"杭州": "hz|79", "宁波": "nb|135", "温州": "wz|330", "金华": "jh|531", "嘉兴": "jx|497", "台州": "tz|403",
                 "绍兴": "sx|355", "湖州": "huzhou|831", "丽水": "lishui|7921", "衢州": "quzhou|6793", "舟山": "zhoushan|8481",
                 "乐清": "yueqingcity|13950", "瑞安": "ruiancity|13951", "义乌": "yiwu|12291", "余姚": "yuyao|5333",
                 "诸暨": "zhuji|357", "象山": "xiangshanxian|6738", "温岭": "wenling|408", "桐乡": "tongxiang|502",
                 "慈溪": "cixi|5334", "长兴": "changxing|834", "嘉善": "jiashanx|14357", "海宁": "haining|500",
                 "德清": "deqing|835", "东阳": "dongyang|536", "安吉": "anji|836", "苍南": "cangnanxian|7579",
                 "临海": "linhai|407", "永康": "yongkang|537", "玉环": "yuhuan|409", "平湖": "pinghushi|501",
                 "海盐": "haiyan|504", "武义县": "wuyix|14528", "嵊州": "shengzhou|359", "新昌": "xinchang|361",
                 "江山": "jiangshanshi|6796", "平阳": "pingyangxian|7575"},
          "其他": {"中国香港": "hk|2050", "中国澳门": "am|9399", "中国台湾": "tw|2051"},
          "海外": {"洛杉矶": "gllosangeles", "旧金山": "glsanfrancisco", "纽约": "glnewyork", "多伦多": "gltoronto",
                 "温哥华": "glvancouver", "伦敦": "glgreaterlondon", "莫斯科": "glmoscow", "首尔": "glseoul", "东京": "gltokyo",
                 "新加坡": "glsingapore", "曼谷": "glbangkok", "清迈": "glchiangmai", "迪拜": "gldubai", "奥克兰": "glauckland",
                 "悉尼": "glsydney", "墨尔本": "glmelbourne", "其他海外城市": "city"}}
city_type_dict = {"生意转让": "/shengyizr/0/", "商铺": "/shangpucz/0/", "厂房": "/changfang/0/", "写字楼": "/zhaozu/0/"}

# 代理ip
ip_url = "http://xxx.xxx.xxx.xxx/xxxx.php"  # 应屏蔽代理API地址
# 类型编码
cateId = 0
# housetype = 4
merchant_url = ""
type_text = ""
# 间隔多久，更新IP
jl_time = time.time()
proxies_ip_lists = []
shiyong_ip=''
shixiao_ip=''
ip_lock=False
proxies = {}
# 执行状况
# 1为入库  2为等待    0位暂停
implementation_status = 0
# 帖子是否��新的状态 1 新     0旧
xt_status = 0
# 用户城市id
cityId = 0
# 重启程序时间
trigger_rerun_time = time.time()

class MySQL_POOL:
    def __init__(self, host, user, password, db):
        self.pool = PooledDB(MySQLdb, mincached=2, maxconnections=20, host=host, user=user,
                             passwd=password, db=db,
                             port=3306, charset='utf8', use_unicode=True)

    def select_one(self, sql):
        conn = self.pool.connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result

    def insert(self, sql):
        try:
            conn = self.pool.connection()
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            return {'result': True, 'id': int(cursor.lastrowid)}
        except Exception as err:
            conn.rollback()
            return {'result': False, 'err': err}
        finally:
            cursor.close()
            conn.close()


class MyThread(threading.Thread):
    """继承Thread类重写run方法创建新进程"""

    def __init__(self, func, args):
        """

        :param func: run方法中要调用的函数名
        :param args: func函数所需的参数
        """
        threading.Thread.__init__(self)
        self.func = func
        self.args = args

    def run(self):
        # print('当前子线程: {}'.format(threading.current_thread().name))
        self.func(self.args[0], self.args[1])
        # 调用func函数
        # 因为这里的func函数其实是上述的main()函数，它需要2个参数；args传入的是个参数元组，拆解开来传入


def get_date_time(out_time):
    """
    :param out_time:传入时间戳
    :return: 返回日期
    """
    # 使用time
    timeStamp = out_time
    timeArray = time.localtime(timeStamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime


def get_time_date(in_date):
    """
    :param in_date:日期时间
    :return: 时间戳
    """
    ts = time.mktime(time.strptime(in_date, "%Y-%m-%d %H:%M:%S"))
    # print(ts)
    return ts


def get_today_time():
    """
    获取当天00:00的时间戳
    :return:
    """
    day_time = int(time.mktime(datetime.date.today().timetuple()))
    return day_time


def header_UA():
    # with open("./user.txt", "r") as f:
    #     UA_lists = f.readlines()
    UA_lists = [
        "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1\n"]
    # print(UA_lists[random.randint(0, len(UA_lists) - 1)][:-2])
    return UA_lists[random.randint(0, len(UA_lists) - 1)][:-2]


def roxies_ip(url, sleep_num=5):
    global proxies_ip_lists,shiyong_ip,ip_lock

    if ip_lock:
        print("等待线程更换IP----")
        sleep(sleep_num)
    if shiyong_ip!='':
        print("使用同线程IP----", shiyong_ip)
        return shiyong_ip
    ip_lock=True
    print("当前状态1----", str(ip_lock))
    print("锁定----",shiyong_ip)
    print(proxies_ip_lists)
    if len(proxies_ip_lists) <= 1:
        for _ in range(1):
            print("更新IP----")
            print("当前状态2----", str(ip_lock)+str(_))
            if shiyong_ip!='':
                continue
            ip = requests.get(url).text.split("\r\n")
            print("IP页面{}".format(ip))
            if "请求过于频繁" in str(ip) or "was not found on this server" in str(ip):
                print("速率超过限制")
                sleep(sleep_num)
                continue
            else:
                # proxies = {'https': "//" + ip}
                proxies_ip_lists = []
                for i in ip:
                    if i=='':
                        continue
                    proxies_ip_lists.append({'https':"//" + i})
                proxies = proxies_ip_lists[0]
                shiyong_ip = proxies
                print("解锁11----", shiyong_ip)
                ip_lock = False
                print("设置线程IP11----", proxies)
                print("切换IP11----", proxies)
                return proxies
    ip_lock = False
    proxies_ip_lists.pop(0)
    proxies = proxies_ip_lists[0]
    shiyong_ip=proxies
    print("解锁22----", shiyong_ip)
    print("设置线程IP22----", proxies)
    print("切换IP22----", proxies)
    return proxies


def get_page_info(url, proxies=""):
    global cateId, merchant_url, type_text,shiyong_ip
    """
    分析58页面信息
    :param url: 页面链接
    :return: 返回页面中的所有链接
    """
    headers = {
        # "cookie": "xxzl_smartid=36ee36cdb08a0a1fff6d5e844849e051; xxzl_deviceid=hKYoijMxUXy%2FqCodkmMptkdD3QLzGOkfFsAgNSu1sT2T%2BeBKGl1SXuqdZW1RHQHb",
        "cookie": "",
        "referer": "https://callback.58.com/",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-site",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": header_UA(),
    }
    for _ in range(5):
        try:
            # responses = requests.get(url,headers=headers, timeout=30)
            responses = requests.get(url, proxies=proxies, headers=headers, timeout=10)
            responses.encoding = "utf-8"
            html = responses.text.encode('gbk', 'ignore').decode('gbk')
            if "访问过于频繁" in html:
                if shiyong_ip!='' and shiyong_ip==proxies:
                    shiyong_ip=''
                print("获取列表中·····访问过于频繁",proxies)
                proxies = roxies_ip(ip_url)
                continue
            # print(html)
            # page_info_url_list = re.findall(r'<a href="(.*?)"', html)
            page_info_img = re.findall(r'data-src\="(.*?)"', html)

            page_info_title = re.findall(r'''class='title'>(.*?)</p>''', html)
            soup = BeautifulSoup(html, "lxml")
            page_info_mark = soup.select(".mark")
            # if not page_info_url_list:
            #     page_info_url_list = re.findall(r'''class='link'.*?href="(.*?)"''', html, re.DOTALL)

            page_info_url_list = []
            for li in soup.select('ul .item>.link'):
                page_info_url_list.append(li.get('href'))
            user_info_url_list = []
            for li in soup.select('ul .item'):
                if li.get('logr')!='':
                    user_info_url_list.append(li.get('logr'))
            user_info_id_list={}
            for li in user_info_url_list:
                user_info_id_list[li.split("_")[3]]=li.split("_")[2]
            page_info_title = []
            for li in soup.select('.item p.title'):
                page_info_title.append(li.get_text())
            page_info_img = []
            for li in soup.select('.item .pic'):
                page_info_img.append(li.get('bg-src'))
            type_text = ''
            if "租商铺" in type_text or 'shangpu' in url:
                type_text = "租商铺"
                housetype = 4
                merchant_url = "https://my.58.com/person/houselist?cityId={}&brokerId=&userId={}&cateId=14&fangwuType=1&pageIndex=1&type=1"
                cateId = 14
            elif "租写字楼" in type_text or 'zhaozu' in url:
                type_text = "租写字楼"
                housetype = 5
                merchant_url = "https://my.58.com/person/houselist?cityId={}&brokerId=&userId={}&cateId=13&fangwuType=1&pageIndex=1&type=1"
                cateId = 13
            elif "租厂房" in type_text or 'changfang' in url:
                type_text = "租厂房"
                housetype = 7
                merchant_url = "https://my.58.com/person/houselist?cityId={}&brokerId=&userId={}&cateId=15&fangwuType=1&pageIndex=1&type=1"
                cateId = 15
            elif "生意转让" in type_text or 'shengyizr' in url:
                type_text = "生意转让"
                housetype = 6
                merchant_url = "https://my.58.com/person/houselist?cityId={}&brokerId=&userId={}&cateId=14&fangwuType=&pageIndex=1&type=3"
                cateId = 14

            print(cateId)
            print(page_info_url_list)
            print(page_info_img)
            print(page_info_mark)
            print('打印uid')
            print(user_info_id_list)
            return page_info_img, page_info_url_list, page_info_title, page_info_mark, housetype,user_info_id_list
        except Exception as e:
            print(e)
            # sleep(4)
            print("IP异常！重新获取IP",proxies)
            if shiyong_ip != '' and shiyong_ip==proxies:
                shiyong_ip = ''
            proxies = roxies_ip(ip_url)


def parse_single_data(url, housetype):
    """
    解析单个页面的数据信息
    :param url: 单个页面的链接
    :param url: 个人信息链��
    :return: 返回数据
    标题，面积，房租，押金，链接，转让费，浏览量，位置，区域，行业，城市，浏览量，卖家ID- 电话，姓名，详情，更新时间戳
    """
    global cityId,shiyong_ip
    for _ in range(10):
        # try:
        headers = {
            "cookie": "",
            "referer": "https://callback.58.com/",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-site",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": header_UA(),
        }
        try:
            responses = requests.get(url, headers=headers, timeout=10)
        except requests.exceptions.ConnectTimeout:
            # proxies = roxies_ip(ip_url)
            print("requests.exceptions.ConnectTimeout")
            continue
        except requests.exceptions.ProxyError:
            # proxies = roxies_ip(ip_url)
            print("requests.exceptions.ProxyError")
            continue
        except requests.exceptions.ReadTimeout:
            print("requests.exceptions.ReadTimeout")
            continue
        responses.encoding = "utf-8"
        html = responses.text.encode('gbk', 'ignore').decode('gbk')
        if "访问过于频繁，本次访问做以下验证码校验" not in html:
            print(f"城市类型：{housetype}")
            script_text = html
            cityId = re.search(r'"area":"(.*?)"', script_text).group(1)
            title = re.search(r'"infotitle":"(.*?)",', script_text).group(1)

            if housetype == 7 or housetype == 4:
                try:
                    rent = re.search(r'"sumprice":"(.*?)",', str(script_text)).group(1).split("元")[0]
                except ValueError:
                    rent = re.search(r'"sumprice":"(.*?)",', str(script_text)).group(1).split("万")[0]

            else:
                try:
                    rent = re.search(r'"price":"(.*?)",', str(script_text)).group(1).split("元")[0]
                except ValueError:
                    rent = re.search(r'"price":"(.*?)",', str(script_text)).group(1).split("万")[0]

            transfer = re.search(r'"transferprice":"(.*?)",', str(script_text)).group(1)
            try:
                area_2 = str(re.search(r'"quyu":"(.*?)",', str(script_text)).group(1)).split("-")[1]
            except IndexError:
                area_2 = str(re.search(r'"quyu":"(.*?)",', str(script_text)).group(1))

            if housetype == 6:
                zrf = re.search(r'"transferprice":"(.*?)",', str(script_text)).group(1)
                area = re.search(r'"area":"(.*?)",', str(script_text)).group(1)
            else:
                try:
                    area = re.search(r'"area":"(.*?)",', str(script_text)).group(1)
                except AttributeError:
                    area = re.search(r'"area":"(.*?)"', str(script_text)).group(1)
                zrf = ""
            zrf = re.sub("\D", "", zrf)
            rent = re.sub("\D", "", rent)

            try:
                industry = "类型:" + re.search(r'"shopIndustry":"(.*?)"', str(script_text)).group(1)
            except AttributeError:
                industry = "类型:未知"
            city = str(re.search(r'"quyu":"(.*?)",', str(script_text)).group(1)).split("-")[0]
            user_id = re.search(r"'userid':'(.*?)',", script_text).group(1)
            pageviews = re.search(r'"visitnum":"(.*?)",', script_text).group(1)
            verify_url_id = url.split("/")[-1]
            try:
                xq = re.search(r'"content":"(.*?)",', script_text).group(1)
            except AttributeError:
                xq = ""
            city_text = re.search(r'"locallist":\[{"name":"(.*?)"', script_text).group(1)
            print(cityId, title, rent, transfer, area_2, zrf, city, user_id, verify_url_id, xq, city_text)
            update_date = int(time.time())
            # 通过商家id，获取电话，姓名
            # contactperson
            name = re.search(r'"contactperson":"(.*?)",', str(script_text)).group(1)
            phone = ""

            # phone, name = parse_personal_information(merchant_url.format(cityId, user_id), verify_url_id, proxies)
            dict_data = {
                    "title": title,
                    "area": area,
                    "rent": rent,
                    "url": url,
                    "transfer": transfer,
                    "area_2": area_2,
                    "industry": industry,
                    "city": city,
                    "pageviews": pageviews,
                    "user_id": user_id,
                    "phone": phone,
                    "name": name,
                    "xq": xq,
                    "update_date": int(update_date),
                    "city_text": city_text,
                    "xt": xt_status,
                    "wuba": url,
                    "zrf": zrf,
                    "house_type": housetype,
                }
            print(dict_data)
            return dict_data
        else:
            print("IP失效！访问过于频繁，本次访问做以下验证码校验!")
            proxies = roxies_ip(ip_url)
            continue
        # except:
        #     print("IP异常！重新获取IP")
        #     proxies = roxies_ip(ip_url)



def parse_personal_information(url, verify_url_id, proxies=""):
    global shiyong_ip
    """
    解析个人信息
    根据id还有用户填写的标题，
    :param url: 个人信息链接
    :param proxies: 代理ip
    :param verify_url_id: 匹配商铺号
    :return: 联系人 电话
    """
    # print(url)
    headers = {
        "cookie": "",
        "referer": "https://callback.58.com/",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-site",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": header_UA(),
    }
    # print(url)
    for _ in range(5):
        try:
            try:
                responses = requests.get(url, proxies=proxies, headers=headers, timeout=10)
                responses.encoding = "utf-8"
                html = responses.text.encode('gbk', 'ignore').decode('gbk')
                # print(html)
                # print(json.loads(html))
                infoList = json.loads(html)["data"]["infoList"]
                for info in infoList:
                    if verify_url_id in info["jumpUrl"]:
                        # print(info["jumpUrl"])
                        phone, name = info["phone"], info["lianxiren"]
                # print(phone, name)
                return phone, name
            except requests.exceptions.ProxyError:
                if shiyong_ip!='' and shiyong_ip==proxies:
                    shiyong_ip=''
                print('信息-----')
                proxies = roxies_ip(ip_url)
                continue
            except urllib3.exceptions.LocationParseError:
                if shiyong_ip!='' and shiyong_ip==proxies:
                    shiyong_ip=''
                print('信息1-----')
                proxies = roxies_ip(ip_url)
                continue
            except requests.exceptions.ConnectTimeout:
                if shiyong_ip!='' and shiyong_ip==proxies:
                    shiyong_ip=''
                print('信息2-----')
                proxies = roxies_ip(ip_url)
                continue
        except json.decoder.JSONDecodeError:
            if shiyong_ip!= '' and shiyong_ip==proxies:
                shiyong_ip = ''
            print('信息3-----')
            proxies = roxies_ip(ip_url)
            continue


def if_data_in_databases(if_info_url, housetype,house_id,user_id):
    """
    :param if_info_url: 判断数据库是否有该条数据的链接
    :return:
    """
    now_time = int(time.time())
    if housetype != 6:
        table_name = 'ims_weixinmao_house_lethouseinfo'
    elif housetype == 6:
        table_name = 'ims_weixinmao_house_oldhouseinfo'
    global mysql_pool

    sql = "select createtime, xt, addtime,tel from {} where houid = {} order by id " \
          "DESC limit 1".format(table_name, house_id)
    results = mysql_pool.select_one(sql)

    # print("打印数据-{}".format(results))
    # conn.commit()
    if results:
        xt_status = results[1]
        add_time = results[2].strftime('%Y-%m-%d %H:%M:%S')
        today_time = get_today_time()
        print("today_time:{}".format(today_time))
        print("add_time:{}".format(int(get_time_date(add_time))))
        if today_time > int(get_time_date(add_time)):
            """今天时间戳大于最后一条数据的日期，那么就是昨天的数据，将状态设置为重复的"""
            print("最后一条数据已是昨天数据，需要更新数据状态！")
            sql = "delete from {} where houid = {} ".format(table_name, house_id)
            mysql_pool.insert(sql)
            return 0, 0,results[3]
        elif now_time-results[0] > (60 * 60 * 72):
            """日期是今天的，那么判断是否超过5小时，5小时内不处理"""
            print("不需要更新详细信息-----")
            return 1, xt_status,''
        else:
            sql = "delete from {} where houid = {} ".format(table_name, house_id)
            mysql_pool.insert(sql)
            """既是今天，但已经超过5小时，需要更新数据"""
            print("需要更新详细信息")
            result = 0
            return result, xt_status,results[3]
    else:
        if user_id!='':
            sql = "select createtime, xt, addtime from {} where user_id = {} order by id " \
                  "DESC limit 1".format(table_name, user_id)
            results = mysql_pool.select_one(sql)
            if results:
                xt_status = results[1]
                add_time = results[2].strftime('%Y-%m-%d %H:%M:%S')
                if now_time-results[0] >  (60 * 60 * 72):
                    return 0, 0,''
                else:
                    result = 0
                    return 1, xt_status,''
            else:
                print("需要更新详细信息")
                result = 0
                xt_status = 1
                return result, xt_status,''
        else:
            print("需要更新详细信息")
            result = 0
            xt_status = 1
            return result, xt_status,''


def conn_sql(dict_data, if_info_url, xt_status):
    """
    插入数据库一条新的数据
    :param dict_data: 字典数据
    :return:
    """
    if dict_data["house_type"] != 6:
        # 商铺 写字楼 厂房     ims_weixinmao_house_lethouseinfo
        # 商铺4，写字楼5，厂房7
        table_name = 'ims_weixinmao_house_lethouseinfo'
    elif dict_data["house_type"] == 6:
        # 其他使用  ims_weixinmao_house_oldhouseinfo
        # 生意转让6
        table_name = "ims_weixinmao_house_oldhouseinfo"

    # 先查询手机号码是否存在，存在则
    # conn.commit()
    if "面议" in str(dict_data["rent"]):
        dict_data["rent"] = 0
    if "无转让费" in dict_data["zrf"]:
        dict_data["zrf"] = 0
    global mysql_pool
    for _ in range(5):
        global conn
        try:
            post={
                'adtype':0,
                'app':'luna',
                'cityid':1029,
                'dispcateid':14,
                'infoid':dict_data["url_id"],
                'hugid':dict_data["house_id"],
                'personaltype':0,
                'timestamp':str(int(time.time()*1000)),
                'type':'call',
                'userid':-2
            }
            url='https://luna.58.com/api/v2/phone/house/get?adtype=0&app=luna&cityid=1029&dispcateid=14&hugid='+dict_data["house_id"]+'&infoid='+dict_data["url_id"]+'&personaltype=0&timestamp='+post['timestamp']+'&type=call&userid=-2'
            sign = 'xxxxxxxxxxxx'  # 应屏蔽签名密钥
            sign=hashlib.md5(sign.encode('utf8')).hexdigest()
            url+='&sign='+sign
            cookie=''
            with open("ck.txt", "r")as f:
                cookie =f.readline()
            ph = requests.get(url, headers={
                'cookie':cookie
            }, timeout=10)
            ph=json.loads(ph.text)
            print(url)
            print('获取号码')
            print(ph)
            if ph and ph['code']==1:
                dict_data["phone"]=ph['data']['virtualNumber']
                print(dict_data)
        except requests.exceptions.ConnectTimeout:
            # proxies = roxies_ip(ip_url)
            print("requests.exceptions.ConnectTimeout")
        except requests.exceptions.ProxyError:
            # proxies = roxies_ip(ip_url)
            print("requests.exceptions.ProxyError")
        except requests.exceptions.ReadTimeout:
            print("requests.exceptions.ReadTimeout")
        if dict_data["house_type"] != 6:
            # 商铺 写字楼 厂房     ims_weixinmao_house_lethouseinfo
            # 商铺4，写字楼5，厂房7
            sql = "INSERT INTO %s(title, addtime, createtime, name, tel, money, direction, address, pic, area, cityname, areaname, housetype, lla, xt, xq, wuba,houid,user_id) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', %s, %s, '%s', '%s', '%s', '%s')" % (
                table_name, dict_data["title"], get_date_time(int(time.time())), dict_data["update_date"],
                dict_data["name"], dict_data["phone"], dict_data["rent"], dict_data["industry"], dict_data["area_2"],
                dict_data["img_url"], dict_data["area"], dict_data["city_text"], dict_data["city"],
                dict_data["house_type"],
                dict_data["pageviews"], xt_status, dict_data["xq"], dict_data["wuba"],dict_data["house_id"],dict_data["user_id"])
        elif dict_data["house_type"] == 6:
            # 其他使用  ims_weixinmao_house_oldhouseinfo
            # 生意转让6
            sql = "INSERT INTO %s(title, addtime, createtime, name, tel, saleprice, perprice, direction, address, pic, area, cityname, areaname, housetype, lla, xt, xq, wuba,houid,user_id) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', %s, %s, '%s', '%s', '%s', '%s')" \
                  % (table_name, dict_data["title"], get_date_time(int(time.time())), dict_data["update_date"],
                     dict_data["name"], dict_data["phone"], dict_data["zrf"], dict_data["rent"],
                     dict_data["industry"], dict_data["area_2"], dict_data["img_url"], dict_data["area"],
                     dict_data["city_text"], dict_data["city"], dict_data["house_type"], dict_data["pageviews"],
                     xt_status,
                     dict_data["xq"], dict_data["wuba"],dict_data["house_id"],dict_data["user_id"])
        print("插入：" + sql)
        mysql_pool.insert(sql)

        break


def start_up():
    global implementation_status, ip_url, mysql_pool

    with open("database_info.txt", "r", encoding="utf-8")as f:
        database_info = json.loads(f.readline())
    print(database_info)
    localhost = database_info["数据库链接"]
    username = database_info["数据库用户"]
    pwd = database_info["数据库密码"]
    db = database_info["数据库名称"]

    mysql_pool = MySQL_POOL(localhost, username, pwd, db)

    ip_url = input_ip_url.get()
    if implementation_status == 0:
        # print("开始录入")
        # print("测试多线程函数")
        url = input_url.get()
        regular_update_time = input_regular_update_time.get()
        ip_url = input_ip_url.get()
        pqpages = paqu.get()
        url_str = "\n" + str(url).replace(";", "\n")
        if url != "" and regular_update_time != "" and ip_url != "":
            implementation_status = 1
            print("开始入库\n获取{}\n链接间隔时间：{}秒".format(url_str, regular_update_time))
            # messagebox.showinfo("开始入库", "获取{}\n链接间隔时间：{}秒".format(url_str, regular_update_time))
            main(url, int(regular_update_time), ip_url,pqpages)
        else:
            messagebox.showerror("异常", "请检查链接、间隔时间和IP代理是否有误！")
    # else:
    #     messagebox.showerror("异常", "程序以在运行中！\n请先暂停再重新启动！")


def pause_program():
    # print("测试多线程函数")
    global implementation_status
    if implementation_status != 0:
        implementation_status = 0
        # messagebox.showinfo("成功", "成功暂停程序！")
        # print("成功暂停程序！")
        print("*" * 200)
    elif implementation_status == 0:
        messagebox.showerror("异常", "程序已停止\n无需暂停")


def restart_program():
    global restart_status, implementation_status

    # 设置运行状态
    implementation_status = 0

    restart_status = 1
    input_url_jl = input_url.get()
    input_ip_url_jl = input_ip_url.get()
    pqpages = paqu.get()
    input_regular_update_time_jl = input_regular_update_time.get()
    input_regular_windows_time_jl = input_regular_windows_time.get()
    print(input_url_jl, input_ip_url_jl, input_regular_update_time_jl, input_regular_windows_time_jl)
    trigger_direct_rerun = int(checkVar.get())
    # tkinter_windows(trigger_direct_rerun, input_url_jl, input_ip_url_jl, input_regular_update_time_jl,
    #                 input_regular_windows_time_jl)
    jl_data = {
        "trigger_direct_rerun": trigger_direct_rerun,
        "input_url_jl": input_url_jl,
        "pqpages":pqpages,
        "input_ip_url_jl": input_ip_url_jl,
        "input_regular_update_time_jl": input_regular_update_time_jl,
        "input_regular_windows_time_jl": input_regular_windows_time_jl,
    }
    with open("cache.txt", "w+")as f:
        f.write(json.dumps(jl_data))

    # 打开当前文件夹下的程序
    print("程序重启11111")
    thread_it(root.destroy())
    print("程序重启22222")
    thread_it(root.quit())
    print("程序重启33333")
    print("程序重启444444")
    import os
    r_v = thread_it(os.system("58.exe"))
    print("程序重启55555")
    print(r_v)

    # import os, sys
    # python = sys.executable
    # os.execl(python, python, * sys.argv)


def thread_it(func, *args):
    '''将函数打包进线程'''
    # 创建
    t = threading.Thread(target=func, args=args)
    # print("触发多线程")
    # 守护 !!!
    t.setDaemon(True)
    # 启动
    t.start()


def processing_page_data(implementation_status, url):
    with pool_sema:
        for _ in range(10):
            try:
                page_info_img, page_info_url_list, page_info_title, page_info_mark, housetype,user_info_id_list = get_page_info(url)
                print("正在重新获取列表信息！")
                break
            except TypeError:
                pass

        for index, info_url in enumerate(page_info_url_list[::-1]):
            if implementation_status == 1:
                if "置顶" not in str(page_info_mark[index]):
                    print("-" * 200)
                    index_num = len(page_info_url_list) - index - 1
                    print(info_url)
                    if_info_url = info_url.split("x.shtml")[0].split("/")[-1]
                    house_id = info_url.split("houseId=")[1].split("&")[0]
                    url_id = if_info_url
                    info_url_2 = "https://luna.58.com/info/{}".format(url_id)
                    print(info_url_2)
                    dict_data = parse_single_data(info_url_2, housetype)

                    if url_id in user_info_id_list:
                        dict_data["user_id"] = user_info_id_list[url_id]
                    else:
                        dict_data["user_id"] =''
                    re_reslut, xt_status,tel = if_data_in_databases(if_info_url, housetype,house_id,dict_data['user_id'])
                    print("是否需要获取详细页面更新数据：{}".format(re_reslut))
                    print("url_id:{}状态：{}".format(if_info_url, re_reslut))
                    if re_reslut == 1:
                        print(page_info_title[index_num] + "=======暂时不需要更新")
                    else:
                        if tel!='':
                            dict_data["phone"] = tel
                        dict_data["wuba"] = info_url
                        dict_data["img_url"] = page_info_img[index_num]
                        dict_data["url_id"] = url_id
                        dict_data["house_id"] = house_id
                        conn_sql(dict_data, if_info_url, xt_status)
            else:
                return "0"


def main(input_url, regular_update_time, ip_url,pqpages):
    global implementation_status, proxies_ip_lists, trigger_rerun_time, proxies,shiyong_ip
    # 获取代理ip
    ip = requests.get(ip_url).text.split("\r\n")
    # print(ip)
    if "请求过于频繁" not in ip:
        # proxies = {'https': "//" + ip}
        proxies_ip_lists = []
        for i in ip:
            print(i)
            proxies_ip_lists.append({'https': "//" + i})
    proxies = proxies_ip_lists[0]
    # print(proxies_ip_lists)
    # 获取页面所有链接
    # url = "https://xa.58.com/zhaozu/0/pve_1092_0/"
    # 商铺
    # url = "https://xa.58.com/shangpucz/0/"
    # 写字楼
    # url = "https://xa.58.com/zhaozu/0/"
    # 厂房
    # url = "https://xa.58.com/changfang/0/"
    # 生意转让
    # url = "https://xa.58.com/shengyizr/0/"
    int(time.time())
    while 1:
        if implementation_status == 1:
            thread_list = []  # 定义一个列表，向里面追加线程
            for url in input_url.split(";"):
                if url == "":
                    continue
                print(pqpages)
                zurl=url
                for i in range(0,int(pqpages)):
                    url=zurl+'/pn'+str(i+1)+'/'
                    print("当前正在对：{}\t入库".format(url))
                    print("当前第：{}\t页".format(pqpages))
                    m = MyThread(processing_page_data, (implementation_status, url))  # 调用MyThread类，得到一个实例
                    # processing_page_data(implementation_status, url)
                    thread_list.append(m)
                    time.sleep(regular_update_time)
                    # if url == input_url.split(";")[-1]:
                    #     implementation_status = 2
                    #     print("等待{}秒后，再次更新入库".format(regular_update_time))
            for m in thread_list:
                m.start()  # 调用start()方法，开始执行

            for m in thread_list:
                m.join()  # 子线程调用join()方法，使主线程等待子线程运行完毕之后才退出

        elif implementation_status == 2:
            time.sleep(regular_update_time)
            print("已等待{}秒，正在再次更新入库".format(regular_update_time))
            print("重新切换IP----避免IP过期")
            if shiyong_ip != '' and shiyong_ip==proxies:
                shiyong_ip = ''
            proxies = roxies_ip(ip_url)
            implementation_status = 1


def test_btn(*args):
    print(city_1.get())
    cache_text = city_f
    print(cache_text)
    city_2_list = []
    for i in cache_text[city_1.get()]:
        # print(i)
        city_2_list.append(i)
    city_2_tup = tuple(city_2_list)
    print(city_2_tup)
    city_2["value"] = city_2_tup
    city_2.current(0)
    print(city_2.get())


def city_add_event():
    city_1_text = city_1.get()
    city_2_text = city_2.get()
    city_py = city_f[city_1_text][city_2_text].split("|")[0]
    city_type_text = city_type.get()
    city_type_py = city_type_dict[city_type_text]
    city_add_url = "https://{}.58.com{}".format(city_py, city_type_py)
    print(f"添加城市链接：{city_add_url};")

    old_all_city = input_url.get()
    old_all_city += city_add_url + ";"
    print(old_all_city)
    input_url.delete(0, 'end')
    input_url.insert(0, old_all_city)
    with open("cache.txt", "r")as f:
        cache_text = json.loads(f.readline())
    trigger_direct_rerun = cache_text["trigger_direct_rerun"]
    input_url_jl = cache_text["input_url_jl"]
    pqpages = cache_text["pqpages"]
    input_ip_url_jl = cache_text["input_ip_url_jl"]
    input_regular_update_time_jl = cache_text["input_regular_update_time_jl"]
    input_regular_windows_time_jl = cache_text["input_regular_windows_time_jl"]
    jl_data = {
        "trigger_direct_rerun": trigger_direct_rerun,
        "pqpages": pqpages,
        "input_url_jl": old_all_city,
        "input_ip_url_jl": input_ip_url_jl,
        "input_regular_update_time_jl": input_regular_update_time_jl,
        "input_regular_windows_time_jl": input_regular_windows_time_jl,
    }
    with open("cache.txt", "w+")as f:
        f.write(json.dumps(jl_data))
    print("成功添加城市！")


def restart_check_event():
    # global trigger_direct_rerun
    tt = checkVar.get()
    print(tt)


def tkinter_windows():
    global ip_url

    try:
        with open("cache.txt", "r")as f:
            cache_text = json.loads(f.readline())
        print(cache_text)
        trigger_direct_rerun = cache_text["trigger_direct_rerun"]
        input_url_jl = cache_text["input_url_jl"]
        pqpages = cache_text["pqpages"]
        input_ip_url_jl = cache_text["input_ip_url_jl"]
        input_regular_update_time_jl = cache_text["input_regular_update_time_jl"]
        input_regular_windows_time_jl = cache_text["input_regular_windows_time_jl"]
    except FileNotFoundError:
        trigger_direct_rerun = False
        input_url_jl = ""
        pqpages=1
        input_ip_url_jl = ""
        input_regular_update_time_jl = ""
        input_regular_windows_time_jl = ""

    global root, input_url,paqu, input_ip_url, input_regular_update_time, input_regular_windows_time, city_1, city_2, \
        city_type, checkVar, restart_check
    root = tkinter.Tk()
    root.geometry('400x320')
    root.title("58时时入库程序")
    tkinter.Label(root, text="选择城市:").grid(row=0, column=0)
    tkinter.StringVar()
    city_1 = ttk.Combobox(root, values=[], state="readonly", width=10)  # #创建下拉菜单
    city_1.bind("<<ComboboxSelected>>", test_btn)
    city_1.grid(row=0, column=1, sticky='w')

    city_1["value"] = (
        '北京', '上海', '天津', '重庆', '安徽', '福建', '广东', '广西', '贵州', '甘肃', '海南', '河南', '黑龙江', '湖北', '湖南', '河北', '江苏', '江西',
        '吉林',
        '辽宁', '宁夏', '内蒙古', '青海', '山东', '山西', '陕西', '四川', '新疆', '西藏', '云南', '浙江', '其他', '海外')
    city_1.current(0)

    city_2 = ttk.Combobox(root, values=["北京", ], state="readonly", width=10)  # #创建下拉菜单
    city_2.grid(row=0, column=1, columnspan=1)
    # city_2["value"] = ()
    city_2.current(0)

    tkinter.Label(root, text="选择模块:").grid(row=1, column=0)
    tkinter.StringVar()
    city_type = ttk.Combobox(root, values=[], state="readonly", width=10)  # #创建下拉菜单
    city_type.grid(row=1, column=1, sticky='w')

    city_type_list = []
    for key, value in city_type_dict.items():
        city_type_list.append(key)
    city_type["value"] = tuple(city_type_list)
    city_type.current(0)

    city_add_btn = tkinter.Button(root, text="添加城市", height=1, command=city_add_event)
    city_add_btn.grid(row=1, column=1, columnspan=1)

    tkinter.Label(root, text="爬取���接：").grid(row=2, column=0)
    input_url = tkinter.Entry(root, bd=5, width=40)
    input_url.grid(row=2, column=1)
    input_url.insert(0, input_url_jl)


    tkinter.Label(root, text="代理IP：").grid(row=3, column=0)
    input_ip_url = tkinter.Entry(root, bd=5, width=40)
    input_ip_url.grid(row=3, column=1)
    input_ip_url.insert(0, input_ip_url_jl)
    # 设置全局ip代理
    ip_url = input_ip_url.get()

    tkinter.Label(root, text="入库间隔时间：").grid(row=4, column=0)
    input_regular_update_time = tkinter.Entry(width=18)
    input_regular_update_time.grid(row=4, column=1, sticky='w')
    input_regular_update_time.insert(0, input_regular_update_time_jl)
    tkinter.Label(root, text="秒").grid(row=4, column=1, columnspan=2)

    tkinter.Label(root, text="程序重启时间：").grid(row=5, column=0)
    input_regular_windows_time = tkinter.Entry(width=18)
    input_regular_windows_time.grid(row=5, column=1, sticky='w')
    input_regular_windows_time.insert(0, input_regular_windows_time_jl)
    tkinter.Label(root, text="分钟").grid(row=5, column=1, columnspan=2)

    # 启动自动运行
    tkinter.Label(root, text="启动自动运行：").grid(row=6, column=0)
    if trigger_direct_rerun:
        checkVar_value = 1
    else:
        checkVar_value = 0
    checkVar = tkinter.StringVar(value=f"{checkVar_value}")
    restart_check = tkinter.Checkbutton(root, command=restart_check_event, variable=checkVar)
    restart_check.grid(row=6, column=1, sticky='w')

    tkinter.Label(root, text="爬取页数：").grid(row=7, column=0)
    paqu = tkinter.Entry(root, bd=5, width=40)
    paqu.grid(row=7, column=1)
    paqu.insert(0, pqpages)
    # 入库，暂停按钮
    tkinter.Button(root, text="启动", command=lambda: thread_it(start_up)).grid(row=8, column=0)
    tkinter.Button(root, text="重启", command=restart_program).grid(row=8, column=1)

    if trigger_direct_rerun:
        thread_it(start_up)
    tkinter.mainloop()

if __name__ == '__main__':
    max_connections = 20
    pool_sema = threading.BoundedSemaphore(max_connections)  # 或使用Semaphore方法
    tkinter_windows()
```

---
▶ 可以在[关于](https://itxiaozhang.com/about/)或者[这篇文章](https://itxiaozhang.com/about-computer-repair-services-with-me/)找到我的联系方式。
▶ 本网站的部分内容可能来源于网络，仅供大家学习与参考，如有侵权请联系我核实删除。  
▶ **我是小章，目前全职提供电脑维修和IT咨询服务。如果您有任何电脑相关的问题，都可以问我噢。**  
