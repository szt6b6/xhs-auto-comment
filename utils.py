"""
工具函数 - 包含反检测增强的人类行为模拟
"""

import random
import time
import re
import math


def random_delay(min_ms=3000, max_ms=8000):
    """随机延迟"""
    delay = random.randint(min_ms, max_ms) / 1000
    time.sleep(delay)


def parse_template(template, **kwargs):
    """解析话术模板"""
    result = template
    for key, value in kwargs.items():
        result = result.replace(f"{{{{{key}}}}}", str(value))
    return result


def extract_numbers(text):
    """从文本中提取数字"""
    match = re.search(r'\d+', text)
    return int(match.group()) if match else 0


def format_followers(text):
    """格式化粉丝数"""
    if not text:
        return 0
    text = text.strip()
    if '万' in text:
        return int(float(text.replace('万', '')) * 10000)
    return extract_numbers(text)


def is_detected(page):
    """检测是否被风控"""
    captcha_selectors = [
        '.captcha-modal',
        '.verify-modal',
        '[class*="captcha"]',
        '[class*="verify"]',
        '#captcha',
        '.login-qrcode'
    ]

    for selector in captcha_selectors:
        if page.query_selector(selector):
            return True

    if 'captcha' in page.url or 'verify' in page.url:
        return True

    return False


def safe_click(page, selector, timeout=5000):
    """安全点击，带等待"""
    try:
        element = page.wait_for_selector(selector, timeout=timeout)
        if element:
            element.click()
            return True
    except Exception as e:
        print(f"点击失败 {selector}: {e}")
    return False


def safe_fill(page, selector, value, timeout=5000):
    """安全填写，带等待"""
    try:
        element = page.wait_for_selector(selector, timeout=timeout)
        if element:
            element.fill(value)
            return True
    except Exception as e:
        print(f"填写失败 {selector}: {e}")
    return False


def random_choice(seq):
    """随机选择"""
    return random.choice(seq)


def random_uniform(min_val, max_val):
    """随机浮点数"""
    return random.uniform(min_val, max_val)


def random_int(min_val, max_val):
    """随机整数"""
    return random.randint(min_val, max_val)


# ========== 人类行为模拟类 ==========

class HumanTyping:
    """模拟人类打字行为"""

    def __init__(self, page, element):
        self.page = page
        self.element = element

    def type_with_human_behavior(self, text):
        """带人类行为的打字"""
        import config

        self.element.click()
        self.element.fill("")

        for i, char in enumerate(text):
            # 基本打字延迟
            delay = random.randint(config.TYPE_DELAY_MIN, config.TYPE_DELAY_MAX)

            # 模拟思考停顿（标点、单词后）
            if char in '。！？，、；：' and random.random() < 0.4:
                delay += random.randint(100, 300)
            elif char == ' ' or (i > 0 and text[i-1] == ' '):
                if random.random() < config.TYPE_WORD_PAUSE_PROB:
                    delay += random.randint(150, 400)

            # 随机退格纠正
            if random.random() < config.TYPE_CORRECTION_PROB and i > 0:
                self.element.press("Backspace")
                random_delay(50, 100)
                self.element.type(char)
            else:
                self.element.type(char)

            time.sleep(delay / 1000)

        random_delay(300, 800)


class HumanMouse:
    """模拟人类鼠标行为"""

    @staticmethod
    def generate_curve_points(start_x, start_y, end_x, end_y, num_points=10):
        """生成贝塞尔曲线点，模拟自然移动"""
        import config

        # 控制点偏移量
        cp1x = start_x + (end_x - start_x) * 0.3 + random.uniform(-50, 50)
        cp1y = start_y + (end_y - start_y) * 0.1 + random.uniform(-30, 30)
        cp2x = start_x + (end_x - start_x) * 0.7 + random.uniform(-50, 50)
        cp2y = start_y + (end_y - start_y) * 0.9 + random.uniform(-30, 30)

        points = []
        for i in range(num_points):
            t = i / (num_points - 1)
            # 三次贝塞尔曲线
            x = (1-t)**3 * start_x + 3*(1-t)**2*t * cp1x + 3*(1-t)*t**2 * cp2x + t**3 * end_x
            y = (1-t)**3 * start_y + 3*(1-t)**2*t * cp1y + 3*(1-t)*t**2 * cp2y + t**3 * end_y
            points.append((int(x), int(y)))

        return points

    @staticmethod
    def human_move(page, start_x, start_y, end_x, end_y):
        """模拟人类鼠标移动（曲线）"""
        import config

        points = HumanMouse.generate_curve_points(start_x, start_y, end_x, end_y)
        duration = random.randint(config.MOUSE_MOVE_DURATION_MIN, config.MOUSE_MOVE_DURATION_MAX)
        delay_per_point = duration / len(points)

        page.mouse.move(start_x, start_y)
        for x, y in points[1:]:
            page.mouse.move(x, y)
            time.sleep(delay_per_point / 1000)

    @staticmethod
    def random_click_offset():
        """返回点击位置偏移量 (dx, dy)"""
        import config
        offset = config.CLICK_OFFSET_RANGE
        return random.randint(-offset, offset), random.randint(-offset, offset)

    @staticmethod
    def maybe_hover(page, element):
        """可能随机悬停"""
        import config
        if random.random() < config.HOVER_PROB:
            box = element.bounding_box()
            if box:
                x = box['x'] + box['width'] / 2
                y = box['y'] + box['height'] / 2
                page.mouse.move(x, y)
                hover_time = random.uniform(config.HOVER_TIME_MIN, config.HOVER_TIME_MAX)
                time.sleep(hover_time)


class HumanScroll:
    """模拟人类滚动行为"""

    @staticmethod
    def random_scroll(page):
        """随机高度滚动，带渐进减速"""
        import config

        height = random.randint(config.SCROLL_HEIGHT_MIN, config.SCROLL_HEIGHT_MAX)

        # 模拟人类滚动（分段，速度变化）
        segments = random.randint(3, 6)
        for i in range(segments):
            segment_height = height // segments
            # 开头和结尾速度慢，中间快
            if i == 0 or i == segments - 1:
                segment_height = int(segment_height * 0.7)
            else:
                segment_height = int(segment_height * (1 + random.uniform(-0.2, 0.3)))

            page.evaluate(f"window.scrollBy(0, {segment_height})")
            time.sleep(random.uniform(0.1, 0.3))

    @staticmethod
    def maybe_scroll_back(page):
        """偶尔回滑"""
        import config
        if random.random() < config.SCROLL_BACK_PROB:
            back_height = random.randint(100, 300)
            page.evaluate(f"window.scrollBy(0, -{back_height})")
            time.sleep(random.uniform(0.5, 1.5))
            # 再滑回来
            page.evaluate(f"window.scrollBy(0, {back_height // 2})")
            time.sleep(random.uniform(0.3, 0.8))


class HumanBrowse:
    """模拟人类浏览行为"""

    @staticmethod
    def stay_on_page(page, min_sec, max_sec):
        """页面停留模拟浏览"""
        stay_time = random.uniform(min_sec, max_sec)
        start_time = time.time()
        mouse_x, mouse_y = 640, 360  # 初始位置记录
        while time.time() - start_time < stay_time:
            if random.random() < 0.3:
                # 随机轻微移动鼠标
                mouse_x = max(0, min(1279, mouse_x + random.randint(-20, 20)))
                mouse_y = max(0, min(719, mouse_y + random.randint(-10, 10)))
                page.mouse.move(mouse_x, mouse_y)
            time.sleep(random.uniform(1, 3))

    @staticmethod
    def maybe_browse_detail(page, return_callback=None):
        """可能进入详情页浏览"""
        import config
        if random.random() < config.BROWSE_DETAIL_PROB:
            browse_time = random.uniform(config.BROWSE_DETAIL_TIME_MIN, config.BROWSE_DETAIL_TIME_MAX)
            time.sleep(browse_time)
            if return_callback:
                return_callback()
            return True
        return False


class HumanBehavior:
    """综合人类行为管理器"""

    def __init__(self, page):
        self.page = page

    def human_scroll_and_stay(self):
        """滚动后停顿浏览"""
        import config

        HumanScroll.random_scroll(self.page)
        HumanScroll.maybe_scroll_back(self.page)

        # 停顿浏览
        pause_time = random.uniform(config.SCROLL_PAUSE_MIN, config.SCROLL_PAUSE_MAX)
        time.sleep(pause_time)

    def random_mouse_move_to_element(self, element):
        """鼠标自然移动到元素"""
        box = element.bounding_box()
        if not box:
            return

        start_x = random.randint(0, 500)
        start_y = random.randint(0, 500)
        end_x = box['x'] + box['width'] / 2
        end_y = box['y'] + box['height'] / 2

        HumanMouse.human_move(self.page, start_x, start_y, end_x, end_y)

    def random_delay_with_long_break(self):
        """随机延迟，可能有长延迟（休息）"""
        import config

        if random.random() < config.LONG_DELAY_PROB:
            long_delay = random.randint(config.LONG_DELAY_MIN, config.LONG_DELAY_MAX)
            print(f"  休息一会儿... ({long_delay}秒)")
            time.sleep(long_delay)
        else:
            random_delay(config.DELAY_MIN * 1000, config.DELAY_MAX * 1000)

    def should_skip_comment(self):
        """是否跳过本次评论"""
        import config
        return random.random() < config.SKIP_COMMENT_PROB


def get_random_template():
    """从模板列表随机获取一条评论"""
    import config
    if config.COMMENT_TEMPLATES:
        return random.choice(config.COMMENT_TEMPLATES)
    return config.DEFAULT_TEMPLATE


def get_random_user_agent():
    """获取随机User-Agent"""
    import config
    return random.choice(config.FAKE_UA_LIST)