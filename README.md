# 🚀 火箭发射追踪系统

中国及全球火箭发射数据追踪系统，支持筛选、搜索、图表统计和数据导出。

## 功能特性

- 🇨🇳 **中国发射Tab** - 追踪长征系列、快舟、引力等中国火箭
- 🌍 **全球发射Tab** - 追踪SpaceX、ULA、Rocket Lab等全球主要发射
- 📊 **统计图表** - 月度发射趋势、火箭型号分布
- 🔍 **多维筛选** - 按年份、火箭型号、发射场、结果筛选
- 📝 **全文搜索** - 搜索载荷/卫星名称
- 📥 **数据导出** - 支持CSV和JSON格式导出

## 数据来源

- [The Space Devs API](https://thespacedevs.com/) - 国际航天数据API

## 部署

本项目使用 GitHub Pages + GitHub Actions 自动部署。

### 手动部署

```bash
# 1. 克隆仓库
git clone https://github.com/YOUR_USERNAME/rocket-launch-tracker.git
cd rocket-launch-tracker

# 2. 本地预览
python -m http.server 8000
# 访问 http://localhost:8000

# 3. 安装依赖并更新数据
pip install -r requirements.txt
python fetch_data.py

# 4. 推送到GitHub
git add . && git commit -m "Update data"
git push
```

### 自动更新

GitHub Actions 每14天自动执行数据更新。也可手动触发：

1. 进入仓库 **Actions** 页面
2. 选择 **Update Rocket Launch Data** workflow
3. 点击 **Run workflow** 手动执行

## 项目结构

```
rocket-launch-tracker/
├── index.html          # 主页面
├── fetch_data.py       # 数据获取脚本
├── data/
│   ├── china.json      # 中国发射数据
│   └── global.json     # 全球发射数据
├── .github/
│   └── workflows/
│       └── update-data.yml  # 自动更新workflow
└── README.md
```

## 数据字段说明

| 字段 | 说明 |
|------|------|
| date | 发射日期 |
| time | 发射时间（UTC） |
| rocket_model | 火箭型号 |
| launch_site | 发射场 |
| payload | 载荷名称 |
| satellite_count | 卫星数量 |
| satellite_nature | 卫星性质（通信/遥感/导航等） |
| orbit_type | 轨道类型（LEO/GTO/MEO等） |
| result | 发射结果（success/failure/partial） |
| company | 所属单位 |

## 技术栈

- HTML5 + CSS3 + Vanilla JavaScript
- Chart.js 4.x - 图表渲染
- GitHub Pages - 静态托管
- GitHub Actions - 自动数据更新

## License

MIT