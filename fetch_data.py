#!/usr/bin/env python3
"""
火箭发射数据获取脚本
数据源: The Space Devs API (https://thespacedevs.com/)
"""
import json
import urllib.request
import urllib.error
import ssl
from datetime import datetime, timedelta

# 忽略SSL验证（某些环境需要）
ssl._create_default_https_context = ssl._create_unverified_context

API_BASE = "https://ll.thespacedevs.com/2.2.0"
PROXY = "http://172.19.48.1:7890"

def fetch_json(url, use_proxy=False):
    """获取JSON数据"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    req = urllib.request.Request(url, headers=headers)
    
    if use_proxy:
        req.set_proxy(PROXY, 'http')
        req.set_proxy(PROXY, 'https')
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def is_chinese_launch(launch):
    """判断是否为中国火箭发射"""
    location = launch.get('location', '') or ''
    lsp_name = launch.get('lsp_name', '') or ''
    
    # 中国发射场
    chinese_locations = ['China', 'Jiuquan', 'Taiyuan', 'Xichang', 'Wenchang', 'Haiyang']
    chinese_companies = ['China', 'CAS', 'CASC', 'CASC ', 'China Aerospace']
    
    return any(loc in location for loc in chinese_locations) or \
           any(co in lsp_name for co in chinese_companies)

def get_mission_type(mission_type):
    """映射任务类型到中文"""
    mapping = {
        'Earth Science': '地球科学',
        'Communications': '通信',
        'Navigation': '导航',
        'Science': '科学',
        'Technology': '技术验证',
        'Cargo': '货运',
        'Crewed': '载人',
        'Manned': '载人',
        'ISS': '空间站',
        'SpySat': '侦察卫星',
        'Unknown': '未知',
        'Test Flight': '测试飞行',
    }
    return mapping.get(mission_type, mission_type or '未知')

def transform_launch(launch):
    """转换API数据为标准化格式"""
    # 处理载荷信息
    mission = launch.get('mission', '')
    mission_type = launch.get('mission_type', 'Unknown')
    
    # 提取载荷名称（从name字段）
    name = launch.get('name', '')
    # name格式通常是 "Rocket | Payload" 或 "Payload"
    if '|' in name:
        payload = name.split('|')[-1].strip()
    else:
        payload = mission or name
    
    # 判断卫星数量（从mission或name推断）
    satellite_count = 1
    if 'satellite' in name.lower() or 'satellites' in name.lower():
        import re
        match = re.search(r'(\d+)\s+satellite', name, re.IGNORECASE)
        if match:
            satellite_count = int(match.group(1))
    
    # 判断卫星性质
    satellite_nature = get_satellite_nature(mission_type, payload, name)
    
    # 轨道类型
    orbit = launch.get('orbit') or {}
    orbit_name = orbit.get('name', '') if isinstance(orbit, dict) else ''
    orbit_abbrev = get_orbit_abbrev(orbit_name)
    
    # 火箭型号清理
    rocket_model = clean_rocket_name(launch.get('name', ''))
    
    # 发射场清理
    location = launch.get('location', '') or ''
    launch_site = clean_launch_site(location)
    
    # 发射结果
    status = launch.get('status', {}) or {}
    result_map = {
        'Success': 'success',
        'Launch Successful': 'success',
        'Failure': 'failure',
        'Launch Failure': 'failure',
        'Partial Failure': 'partial',
        'TBD': 'TBD',
        'TBC': 'TBC',
        'Go': 'Go',
        'Unknown': 'unknown'
    }
    result = result_map.get(status.get('abbrev', ''), 'unknown')
    
    # 公司
    lsp_name = launch.get('lsp_name', '') or 'Unknown'
    company = get_company_name(lsp_name)
    
    return {
        'id': launch.get('id', ''),
        'date': launch.get('net', '')[:10] if launch.get('net') else '',
        'time': launch.get('net', '')[11:19] if launch.get('net') else '',
        'rocket_model': rocket_model,
        'launch_site': launch_site,
        'payload': payload,
        'satellite_count': satellite_count,
        'satellite_nature': satellite_nature,
        'orbit_type': orbit_abbrev,
        'result': result,
        'company': company,
        'notes': ''
    }

def get_satellite_nature(mission_type, payload, name):
    """判断卫星性质"""
    text = f"{mission_type} {payload} {name}".lower()
    
    if any(k in text for k in ['通信', 'comm', 'starlink', 'internet', 'broadband']):
        return '通信'
    elif any(k in text for k in ['导航', 'nav', 'gps', 'beidou', 'glonass', 'galileo']):
        return '导航'
    elif any(k in text for k in ['遥感', 'remote', 'earth', 'imaging', 'surveillance', 'optical', 'radar']):
        return '遥感'
    elif any(k in text for k in ['科学', 'science', 'experiment', 'test']):
        return '科学实验'
    elif any(k in text for k in ['货运', 'cargo', 'supply']):
        return '货运'
    elif any(k in text for k in ['载人', 'crew', 'manned', 'taikonaut']):
        return '载人'
    elif any(k in text for k in ['气象', 'weather', 'meteorological']):
        return '气象'
    elif any(k in text for k in ['侦察', 'spy', 'military', 'secret']):
        return '军事/侦察'
    else:
        return '其他'

def get_orbit_abbrev(orbit_name):
    """获取轨道缩写"""
    orbit_name = orbit_name.lower()
    if 'leo' in orbit_name:
        return 'LEO'
    elif 'gto' in orbit_name or 'geostationary' in orbit_name:
        return 'GTO'
    elif 'meo' in orbit_name:
        return 'MEO'
    elif 'sso' in orbit_name or 'sun-synchronous' in orbit_name:
        return 'SSO'
    elif 'polar' in orbit_name:
        return 'Polar'
    elif 'iss' in orbit_name or 'space station' in orbit_name:
        return 'ISS'
    elif 'lunar' in orbit_name or 'moon' in orbit_name:
        return 'Lunar'
    elif 'heo' in orbit_name or 'highly elliptical' in orbit_name:
        return 'HEO'
    else:
        return 'LEO'  # 默认为LEO

def clean_rocket_name(name):
    """清理火箭型号名称"""
    # 移除载荷部分
    if '|' in name:
        rocket = name.split('|')[0].strip()
    else:
        rocket = name
    
    # 标准化长征系列
    rocket = rocket.replace('Long March', '长征').replace('LM', '长征')
    rocket = rocket.replace('CZ-', '长征-')
    
    # 标准化其他型号
    rocket = rocket.replace('Falcon 9 Block 5', 'Falcon 9')
    rocket = rocket.replace('Falcon Heavy', 'Falcon Heavy')
    
    return rocket

def clean_launch_site(location):
    """清理发射场名称"""
    location = location or ''
    
    if 'Jiuquan' in location:
        return '酒泉'
    elif 'Taiyuan' in location:
        return '太原'
    elif 'Xichang' in location:
        return '西昌'
    elif 'Wenchang' in location:
        return '文昌'
    elif 'Haiyang' in location:
        return '海阳'
    elif 'Hammaguira' in location:
        return '哈马基拉'
    elif 'Kourou' in location:
        return '库鲁'
    elif 'Cape Canaveral' in location or 'Kennedy' in location:
        return '卡纳维拉尔角'
    elif 'Vandenberg' in location:
        return '范登堡'
    elif 'Baikonur' in location:
        return '拜科努尔'
    elif 'Plesetsk' in location:
        return '普列谢茨克'
    elif 'Tanegashima' in location:
        return '种子岛'
    elif 'MHI' in location or 'Tanegashima' in location:
        return '种子岛'
    elif 'Naro' in location:
        return '罗老'
    elif 'Satish Dhawan' in location:
        return '萨蒂什·达万'
    else:
        return location.split(',')[0].strip()

def get_company_name(lsp_name):
    """获取公司中文名"""
    lsp_name = lsp_name or ''
    
    if 'China Aerospace' in lsp_name or 'CASC' in lsp_name:
        return '中国航天科技集团'
    elif 'China Rocket' in lsp_name:
        return '中国火箭公司'
    elif 'CAS Space' in lsp_name:
        return '中科宇航'
    elif 'SpaceX' in lsp_name:
        return 'SpaceX'
    elif 'ULA' in lsp_name:
        return 'ULA'
    elif 'Rocket Lab' in lsp_name:
        return 'Rocket Lab'
    elif 'Mitsubishi' in lsp_name or 'MHI' in lsp_name:
        return '三菱重工业'
    elif 'ISRO' in lsp_name or 'Antrix' in lsp_name:
        return '印度空间研究组织'
    elif 'Roscosmos' in lsp_name:
        return '俄罗斯联邦航天局'
    elif 'ESA' in lsp_name or 'Ariane' in lsp_name:
        return '欧洲空间局'
    elif 'Northrop' in lsp_name or 'Orbital' in lsp_name:
        return '诺斯罗普·格鲁曼'
    elif 'Blue Origin' in lsp_name:
        return '蓝色起源'
    elif 'Virgin' in lsp_name:
        return '维珍银河'
    elif 'Landspace' in lsp_name:
        return '蓝箭航天'
    elif 'iSpace' in lsp_name or '星际荣耀' in lsp_name:
        return '星际荣耀'
    elif 'ExPace' in lsp_name or '快舟' in lsp_name:
        return '快舟火箭'
    elif 'ZeroG' in lsp_name or '引力' in lsp_name:
        return '引力火箭'
    else:
        return lsp_name

def fetch_launches(start_date, end_date, limit=200):
    """获取指定日期范围的发射数据"""
    all_launches = []
    offset = 0
    batch_size = 50
    
    print(f"Fetching launches from {start_date} to {end_date}...")
    
    while offset < limit:
        url = f"{API_BASE}/launch/previous/?limit={batch_size}&mode=list&offset={offset}"
        # 按时间过滤
        url += f"&net__gte={start_date}&net__lte={end_date}"
        
        data = fetch_json(url)
        if not data or not data.get('results'):
            break
        
        launches = data['results']
        all_launches.extend(launches)
        print(f"  Fetched {len(launches)} launches (total: {len(all_launches)})")
        
        if len(launches) < batch_size:
            break
        
        offset += batch_size
    
    return all_launches

def main():
    # 计算日期范围：2023年1月1日至今
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = '2023-01-01'
    
    print("=== 火箭发射数据获取 ===")
    print(f"日期范围: {start_date} 至 {end_date}")
    
    # 获取所有历史发射数据
    all_launches = fetch_launches(start_date, end_date, limit=500)
    
    print(f"\n总共获取 {len(all_launches)} 条发射记录")
    
    # 分离中国和全球数据
    china_launches = []
    global_launches = []
    
    for launch in all_launches:
        transformed = transform_launch(launch)
        
        if is_chinese_launch(launch):
            china_launches.append(transformed)
            print(f"  [中国] {transformed['date']} | {transformed['rocket_model']} | {transformed['payload'][:30]}")
        else:
            global_launches.append(transformed)
    
    # 按日期排序
    china_launches.sort(key=lambda x: x['date'], reverse=True)
    global_launches.sort(key=lambda x: x['date'], reverse=True)
    
    # 保存数据
    with open('data/china.json', 'w', encoding='utf-8') as f:
        json.dump({
            'last_updated': datetime.now().isoformat(),
            'count': len(china_launches),
            'launches': china_launches
        }, f, ensure_ascii=False, indent=2)
    
    with open('data/global.json', 'w', encoding='utf-8') as f:
        json.dump({
            'last_updated': datetime.now().isoformat(),
            'count': len(global_launches),
            'launches': global_launches
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== 数据已保存 ===")
    print(f"中国发射: {len(china_launches)} 条 -> data/china.json")
    print(f"全球发射: {len(global_launches)} 条 -> data/global.json")

if __name__ == '__main__':
    main()