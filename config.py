"""
配置文件
"""

# 小红书URL
BASE_URL = "https://www.xiaohongshu.com"

# 搜索页容器选择器
CONTAINER_SELECTOR = '''xpath://*[@id="global"]/div[2]/div[2]/div/div/div[3]'''

# 帖子卡片选择器
POST_SELECTOR = '''xpath://*[@id="global"]/div[2]/div[2]/div/div/div[3]/div[1]/section'''

# 评论激活按钮（先点击这个才能出现输入框）
COMMENT_ACTIVATE = '''xpath://*[@id="noteContainer"]/div[4]/div[3]/div/div/div[1]/div[1]/div/div/span'''

# 评论输入框
COMMENT_INPUT = '''xpath://*[@id="content-textarea"]'''

# 发送按钮
COMMENT_SUBMIT = '''xpath://*[@id="noteContainer"]/div[4]/div[3]/div/div/div[2]/div/div[2]/button[1]'''

# 话术模板列表（随机挑选）
COMMENT_TEMPLATES = [
    "写得真好，已收藏👍",
    "这个攻略太实用了，赞一个",
    "学习到了，感谢分享～",
    "姐妹写得超详细！",
    "终于找到了！太开心了",
    "感觉很有用，mark一下",
    "说得太对了！",
    "太棒了，必须点赞",
    "感谢博主的分享～",
    "这个建议太中肯了",
    "同感同感！",
    "博主好用心👍",
    "收藏了收藏了",
    "写得真心不错",
    "点赞支持！",
    "这波必须收藏",
    "博主人美心善",
    "已关注，期待更多内容",
    "太有用了，已存",
    "写得好好，看完了",
]

# 默认话术（如果模板列表为空时使用）
DEFAULT_TEMPLATE = "你好！看了你的笔记很有共鸣，希望能进一步交流~"

# 评论延迟范围（秒）
DELAY_MIN = 3
DELAY_MAX = 8

# ========== 反检测增强配置 ==========

# 主页浏览配置
HOME_PAGE_STAY_MIN = 10  # 进入主页后最少停留时间（秒）
HOME_PAGE_STAY_MAX = 30  # 进入主页后最多停留时间（秒）

# 滚动行为配置
SCROLL_HEIGHT_MIN = 300   # 滚动高度最小值（px）
SCROLL_HEIGHT_MAX = 1000  # 滚动高度最大值（px）
SCROLL_PAUSE_MIN = 2       # 滚动后停顿最小时间（秒）
SCROLL_PAUSE_MAX = 8       # 滚动后停顿最大时间（秒）
SCROLL_BACK_PROB = 0.1     # 回滑概率（10%）

# 浏览行为配置
BROWSE_DETAIL_PROB = 0.15     # 点击进入详情页的概率
BROWSE_DETAIL_TIME_MIN = 5    # 详情页浏览最短时间（秒）
BROWSE_DETAIL_TIME_MAX = 15    # 详情页浏览最长时间（秒）

# 评论行为配置
SKIP_COMMENT_PROB = 0.05   # 跳过评论的概率（5%）
LONG_DELAY_PROB = 0.1      # 长延迟概率（10%）
LONG_DELAY_MIN = 20        # 长延迟最短时间（秒）
LONG_DELAY_MAX = 60        # 长延迟最长时间（秒）

# 打字行为配置
TYPE_DELAY_MIN = 30        # 打字间隔最小（ms）
TYPE_DELAY_MAX = 200       # 打字间隔最大（ms）
TYPE_WORD_PAUSE_PROB = 0.15  # 单词后停顿概率
TYPE_CORRECTION_PROB = 0.05   # 退格纠正概率

# 鼠标行为配置
MOUSE_MOVE_DURATION_MIN = 200   # 鼠标移动最短时间（ms）
MOUSE_MOVE_DURATION_MAX = 800   # 鼠标移动最长时间（ms）
CLICK_OFFSET_RANGE = 3          # 点击位置偏移范围（px）
HOVER_PROB = 0.3                # 点击前悬停概率
HOVER_TIME_MIN = 0.5            # 悬停最短时间（秒）
HOVER_TIME_MAX = 2              # 悬停最长时间（秒）

# 指纹混淆配置
FAKE_UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
]
CANVAS_NOISE_MIN = -5   # Canvas噪声范围
CANVAS_NOISE_MAX = 5
WEBGL_MASK_ENABLED = True
HARDWARE_CONCURRENCY_MIN = 4
HARDWARE_CONCURRENCY_MAX = 16
DEVICE_MEMORY_MIN = 2
DEVICE_MEMORY_MAX = 8

# 检测到验证码后的等待时间（秒）
CAPTCHA_WAIT_TIME = 30

# 最大重试次数
MAX_RETRIES = 3

# 风控处理模式：wait=等待重试，skip=跳过
DETECT_MODE = "wait"

# 浏览器配置
BROWSER_HEADLESS = False
BROWSER_SLOW_MO = 100