# 小红书自动评论工具 - Playwright 自动化（反检测增强版）

## 功能特性

### 人类行为模拟
- **鼠标轨迹**：贝塞尔曲线生成自然移动路径，避免直线移动
- **打字行为**：速度波动、随机停顿、偶尔退格纠正
- **滚动行为**：随机高度、渐进减速、偶尔回滑
- **浏览行为**：页面停留、随机进入详情页、间歇性浏览

### 反检测机制
- **指纹混淆**：Canvas 噪声注入、WebGL 参数随机化、Navigator 属性伪装
- **浏览器特征**：随机 User-Agent、hardwareConcurrency、deviceMemory
- **操作间隔**：长延迟随机、时段不均匀、跳过概率模拟

### 评论区本随机化
- 内置 20 条评论模板，每次随机选择
- 内容差异化（短句/长句/带emoji等）
- 5% 概率跳过本次评论

## 安装依赖

```bash
pip install playwright
playwright install chromium
```

## 项目结构

```
xhs-auto-comment/
├── main.py              # 主入口（间歇性浏览 + 反检测）
├── config.py            # 配置文件（模板列表、反检测参数）
├── browser.py           # 浏览器管理（指纹混淆注入）
├── collector.py         # 帖子采集（间歇性浏览模式）
├── comment.py          # 评论功能（人类行为模拟）
├── utils.py            # 工具函数（鼠标轨迹、打字模拟）
├── search.py           # 搜索功能（保留）
└── README.md
```

## 使用方法

### 基本用法
```bash
python main.py -k "关键词"
```

### 完整参数
```bash
python main.py -k "关键词" --min-posts 5 --max-posts 20 --headless
```

### 参数说明
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-k, --keyword` | 搜索关键词 | 必填 |
| `--min-posts` | 最少采集帖子数 | 5 |
| `--max-posts` | 最多采集帖子数 | 20 |
| `--headless` | 无头模式运行 | False |
| `--no-login` | 跳过登录检查 | False |

## 工作流程

1. **启动浏览器** → 自动加载 cookies 或等待扫码登录
2. **主页浏览** → 进入主页后先自然浏览 10-30 秒
3. **间歇性采集** → 边浏览边采集，滚动 → 停顿 → 再滚动
4. **随机浏览详情** → 15% 概率点击帖子进入详情页浏览 5-15 秒
5. **批量评论** → 每条评论使用随机模板 + 鼠标曲线轨迹
6. **智能延迟** → 评论间隔 3-8 秒，10% 概率触发长延迟（20-60秒）模拟休息

## 反检测配置（config.py）

```python
# 评论模板列表
COMMENT_TEMPLATES = ["写得真好，已收藏👍", "太棒了，必须点赞", ...]

# 主页浏览停留时间
HOME_PAGE_STAY_MIN = 10
HOME_PAGE_STAY_MAX = 30

# 滚动行为
SCROLL_HEIGHT_MIN = 300
SCROLL_HEIGHT_MAX = 1000
SCROLL_PAUSE_MIN = 2
SCROLL_PAUSE_MAX = 8

# 打字行为
TYPE_DELAY_MIN = 30
TYPE_DELAY_MAX = 200
TYPE_CORRECTION_PROB = 0.05

# 指纹混淆
FAKE_UA_LIST = [...]
CANVAS_NOISE_MIN = -5
CANVAS_NOISE_MAX = 5
```

## 注意事项

- 登录成功后会自动保存 cookies，下次启动优先加载
- 检测到验证码会自动暂停等待
- 建议使用 `--headless` 模式进行长时间任务
- 间歇性浏览比批量采集更难被检测为机器人行为